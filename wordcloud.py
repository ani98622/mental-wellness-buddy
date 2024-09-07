import mesop as me
import matplotlib.pyplot as plt
from office_issues import fetch_issue_data, create_connection
from wordcloud import WordCloud

def generate_word_cloud(data):
    # Filter the data to include only issues with a count > 5
    filtered_data = {row[0]: row[1] for row in data if row[1] > 5}

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(filtered_data)

    # Create a matplotlib figure
    fig = plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Hide the axes

    return fig

# Mesop page to display the word cloud
@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/",
    title="Word Cloud of Office Issues"
)
def app():
    # Fetch the issue data
    conn = create_connection()
    data = fetch_issue_data(conn)

    # Generate the word cloud
    fig = generate_word_cloud(data)

    # Display the word cloud using Mesop
    me.text("Word Cloud of Office Issues:")
    me.plot(fig, style=me.Style(width="100%"))
    me.button("Back", on_click=lambda e: me.navigate("/"))

    # Close the database connection when done
    conn.close()
