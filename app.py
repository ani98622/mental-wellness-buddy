from sqlcode import *
import os, socket, subprocess, platform
from dotenv import load_dotenv
import mesop as me, mesop.labs as mel
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from visuals import generate_bar_chart, get_date_range

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

@me.stateclass
class State:
    user_id: str = ""
    password: str = ""
    logged_in: bool = False 
    selected_values: list[str]
    mock_stats : dict[str]  

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

session_chat = ChatMessageHistory()

llm = ChatGroq(model="llama3-8b-8192", api_key = groq_api_key)
s_id = get_system_id()

personal_info = Get_PersonalInfo(s_id = s_id)

if personal_info:
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f""" You should act a good friend. If they need mental support, act accordingly.
                Information about this person giving below. Use it while giving suggestions and its for your better understanding. 
                There might be some of the problems they faced before don't explicitly mention those while responding
                {personal_info}

                Be precise with your response at most 30 - 50 words. Unless you feel large respose is compulsory. Always give some response.
    """,
            ),
            MessagesPlaceholder(variable_name = "messages"),
        ]
    )
else:
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """ You should act a good friend. If they need mental support, act accordingly.
                Be precise with your response at most 30 - 50 words. Unless you feel large respose is compulsory. Always give some response.
    """,
            ),
            MessagesPlaceholder(variable_name = "messages"),
        ]
    )

chain = chat_prompt | llm

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: session_chat,
    input_messages_key="input",
    history_messages_key="messages",
)

def get_sessionchat():
    global session_chat
    return str(session_chat)

def update_info():
    s_id = get_system_id()
    past_info=Get_PersonalInfo(s_id)
    return 

def session_done(session_chat=session_chat, llm = llm):
    s_id = get_system_id()
    chat = get_sessionchat()
    info = give_personalinfo(s_id = s_id, chat = chat, llm = llm)
    Add_Chathistory(s_id = s_id, chat = chat)
    add_data(s_id = s_id, chat = chat, llm = llm)
    UpdateOrAdd_PersonalInfo(s_id = s_id, info = info)
    me.navigate("/")

def give_personalinfo(s_id, chat, llm):
    personal_info = Get_PersonalInfo(s_id = s_id)
    if personal_info:
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f""" If asked for summary, provide an updated personal information. 
                    Personal information may contain a person's details like name, their 
                    likes, interests, hobbies, dislikes etc. It should be in a paragraph of 
                    less than 1990 characters. 
                    
                    Previous personal Information: 
                    {personal_info}
                    
                    Update the above personal info by adding relevant data that you get from below chat:
                    {chat}""",
                ),
            ]
        )
    else:
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f""" If asked for summary, provide a personal summary. 
                    Personal information may contain a person's details like name, their 
                    likes, interests, hobbies, dislikes etc. It should be in a paragraph of 
                    less than 1990 characters. 
                    
                    Give a personal summary by adding relevant data that you can get from below chat:
                    {chat}        """,
                ),
            ]
        )
    chain = chat_prompt | llm
    info = chain.invoke({"input": "summary"}).content
    return info

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
    mel.chat(transform, title="Mindmate", bot_user="Mindmate")
    me.button(label = "Done", on_click=session_done)

def transform(input: str = "", history: list[mel.ChatMessage] = []):
    session_id = get_system_id()
    text =chain_with_message_history.invoke({"input": input}, config={"configurable": {"session_id": session_id}}).content
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
        with me.box(style=me.Style(margin=me.Margin.all(15))):
            me.text(text="Choose Period")
            me.select(
            label="select",
            options=[
                me.SelectOption(label="Last 7 Days", value="Last 7 Days"),
                me.SelectOption(label="Last 30 Days", value="Last 30 Days"),
                me.SelectOption(label="This Month", value="This Month"),
                me.SelectOption(label="Last Month", value="Last Month")
            ],
            on_selection_change=on_selection_change,
            style=me.Style(width=500),
            multiple=False,
            )
        state = me.state(State)
        from_date_str, till_date_str = get_date_range(state.selected_values)

        data = Get_Stats(from_date_str, till_date_str) 
        if data:
            fig = generate_bar_chart(result = data, title = 'Results')
            me.text("Office Issue Statistics:")
            me.plot(fig, style=me.Style(width="80%"))
        else:
            me.text("No data available for the selected period.")
        me.button("Back", on_click=lambda e: me.navigate("/Hr/dashboard"),type = 'flat')
    else:
        me.navigate("")

def on_selection_change(e: me.SelectSelectionChangeEvent):
    s = me.state(State)
    s.selected_values = e.values

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
            user = Admin_Login(state.user_id, state.password)
            if user == True:
                state.logged_in = True
                me.navigate("/Hr/dashboard")
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