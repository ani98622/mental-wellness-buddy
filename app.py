import os, socket,subprocess,platform
from dotenv import load_dotenv
import mesop as me
import mesop.labs as mel
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from admin import validate_user
from office_issues import fetch_issue_data, create_connection
from visuals import generate_bar_chart

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))  
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def is_office_network(ip_address):
    office_ip_range_start = '172.16.2.100'
    office_ip_range_end = '172.16.2.300'

    ip_num = int(''.join([f"{int(part):02x}" for part in ip_address.split('.')]), 16)
    start_num = int(''.join([f"{int(part):02x}" for part in office_ip_range_start.split('.')]), 16)
    end_num = int(''.join([f"{int(part):02x}" for part in office_ip_range_end.split('.')]), 16)

    return start_num <= ip_num <= end_num

@me.stateclass
class State:
    user_id: str = ""
    password: str = ""
    logged_in: bool = False  

def remove_domain(email, domain="@agilisium.com"):
    if email.endswith(domain):
        return email.replace(domain, "")
    return email

def on_user_id_input(e: me.InputEvent):
    state = me.state(State)
    state.user_id = e.value
    state.user_id = remove_domain(state.user_id)

def on_password_input(e: me.InputEvent):
    state = me.state(State)
    state.password = e.value  

def get_system_id():
    system = platform.system()
    
    if system == 'Windows':
        try:
            output = os.popen('wmic csproduct get uuid').read().strip()
            uuid = output.split('\n')[1].strip() if len(output.split('\n')) > 1 else None
            if uuid:
                return uuid
            else:
                return "UUID not found or command output is empty."
        except Exception as e:
            return f"An error occurred on Windows: {e}"
    
    elif system == 'Darwin':  
        try:
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'Hardware UUID' in line:
                    return line.split(': ')[1].strip()
            return "Hardware UUID not found."
        except Exception as e:
            return f"An error occurred on macOS: {e}"
    else:
        return "Unsupported operating system."

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id,"sqlite:///database.db")

llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """ You are a very compassionate and supportive assistant designed to help and pacify employees struggling with depression. 
                Stick to the issues he/she is suffering from while replying. Don't answer questions unrelated to mental health issues.
                Don't give very big answers, keep it short and effective.
                Your goal is to offer empathetic, non-judgmental guidance and provide actionable advice to improve their mental well-being.
                Keep in mind that all the employees are in INDIA. 
                When responding, consider the following:

                Empathy: Start by acknowledging the person's feelings without minimizing their experience. Act like you are the Girlfriend/Boyfriend/Mother/Father/Close Friend whom a person can share thoughts freely. 
                Active Listening: Encourage the person to share their thoughts and feelings, and validate their emotions.
                Positive Reinforcement: Highlight their strengths and remind them of their worth.
                Coping Strategies: Suggest healthy coping mechanisms, such as deep breathing exercises, journaling, physical activity, suggest some games of his likings to play or speaking with a mental health professional.
                Encouragement: Motivate them to seek support from loved ones and professionals if needed.
                Safety Net: If you sense that the person may be at risk of harming themselves in anyway like suiciding, encourage them to contact a trusted person or professional immediately.
                Remember, anonymity is the most important thing. You are not supposed to reveal anyone's ID, NAME, Email Address, system ID, etc in any case to others.
                Remember, your responses should be gentle, understanding, and focused on offering hope and practical steps toward feeling better.
                Remember, you are here to help, not to provide answers. Feel free to ask clarifying questions or seek additional support as needed.
                
                Note : 
                1- You are made to assist Human Resource Department(HRD) to anonymously encounter the issues/mental health of the employees so that regulatory measures can be taken.
                Owing to which you have to help summarizing the category of problem he is facing also later on but not to the user. 
                2- Respond keeping his/her previous chats in mind.
                3- You can also use famous quotes by psychologists and others successful people to motivate them.
""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

runnable = prompt | llm
runnable_with_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

def on_load(e: me.LoadEvent):
    me.set_theme_mode("system")

@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io", "https://huggingface.co"]
    ),
    path="/main_page/chat_bot",
    title="Mesop Demo Chat",
    on_load=on_load,
)

def chat_page():
    mel.chat(transform, title="Med Buddy", bot_user="Mesop Bot")
    me.button("back", on_click=lambda e: me.navigate("/"), type="flat")

def transform(input: str = "", history: list[mel.ChatMessage] = []):
    session_id = get_system_id()
    text = runnable_with_history.invoke({"input": input}, config={"configurable": {"session_id": session_id}}).content
    return text

@me.page(path="/Hr/dashboard")
def hr_dashboard_page():
    state = me.state(State)
    if state.user_id and state.password:
        me.text("Login successful! Redirecting...", type="headline-4") # problem
        me.text("Welcome to the HR Dashboard!", type="headline-4")
        me.text("Here you can access confidential HR information and reports.", type="body-1")
        me.button("Bar Plot", on_click=lambda e: me.navigate("/Hr/barplot"), type="flat")
        me.button("Logout", on_click=clear_login, type="flat")
    else:
        me.navigate("")

@me.page(path="/Hr/barplot")
def barplot_page():
    state = me.state(State)
    if state.user_id and state.password:
        conn = create_connection()
        data = fetch_issue_data(conn)
        fig = generate_bar_chart(data)
        me.plot(fig, style=me.Style(width="80%"))
        me.button("Back", on_click=lambda e: me.navigate("/Hr/dashboard"),type="flat")
    else:
        me.navigate("")

@me.page(path="/Hr/try_again")
def try_again_page():
    state = me.state(State)
    if state.user_id and state.password:
        me.text("Invalid credentials. Please try again.", type="headline-4")
        me.button("Try Again", on_click=clear_login,type="flat")
        me.button("Home", on_click=lambda e: me.navigate("/"),type="flat")
    else:
        me.navigate("")

def clear_login(e: me.ClickEvent):
        state = me.state(State)

        if state.user_id and state.password:
            state.user_id=""
            state.password=""
            me.navigate("/Hr")
           
@me.page(path="/Hr")
def hr_login_page():
    state = me.state(State)
    me.text("HR Login", type="headline-4")
    me.text("Enter your HR credentials to access the dashboard.", type="body-1")

    me.input(label="Username", on_input=on_user_id_input)  
    me.input(label="Password", type="password", on_input=on_password_input)  
    
    def handle_login(e: me.ClickEvent):
        state = me.state(State)

        if state.user_id and state.password:
            
            user = validate_user(state.user_id, state.password)
            if user:
                if user[2] == state.password:
                    state.logged_in = True
                    me.navigate("/Hr/dashboard")
                else:
                    me.navigate("/Hr/try_again")
            else:
                me.navigate("/Hr/try_again")

    me.button("Login", on_click=handle_login, type="flat")
    me.button("back", on_click=lambda e: me.navigate("/"), type="flat")

@me.page(path="/")
def main_page():
    me.text("Welcome to Med Buddy!", type="headline-2")
    user_ip = get_ip_address()
    if is_office_network(user_ip):
        with me.box(style=me.Style(display="flex", flex_direction="column", gap=20)):
            me.button("Start Chatting", on_click=lambda e: me.navigate("/main_page/chat_bot"), type="flat", color="accent")
            me.button("HR Login", on_click=lambda e: me.navigate("/Hr"), type="flat", color="accent")
    else:
        me.text("Access denied. Please connect to the office Wi-Fi.",type="headline-3")