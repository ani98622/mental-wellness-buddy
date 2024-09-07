import mesop as me
import matplotlib.pyplot as plt
from office_issues import fetch_issue_data, create_connection
from matplotlib.figure import Figure

def generate_bar_chart(data):
    # Extract labels and values from data
    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    # Create a bar chart using matplotlib
    fig = Figure(figsize=(6, 4))  # Specify the figure size
    ax = fig.subplots()
    ax.bar(labels, values)
    
    # Set layout properties
    ax.set_xlabel("Issues")
    ax.set_ylabel("Count")
    ax.set_title("Prevalence of Issues in the Office")
    
    # Rotate the x-axis labels for better readability
    ax.set_xticklabels(labels, rotation=45, ha="right")
    
    # Adjust layout for better appearance
    fig.tight_layout()

    return fig

# Mesop page to display the bar chart
@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Office Issue Prevalence"
)
def app():
    # Fetch the issue data
    conn = create_connection()
    data = fetch_issue_data(conn)

    # Generate the bar chart
    fig = generate_bar_chart(data)

    # Display the bar chart using Mesop
    me.text("Office Issue Prevalence:")
    me.plot(fig, style=me.Style(width="80%"))
    me.button("Back", on_click=lambda e: me.navigate("/"))
