# Reddit research agent using OpenAI's GPT and Dendrite SDK:
# 1. Take in a prompt like "What are people's opinions on CrewAI? Do people like it?"
# 2. Searches Reddit for relevant posts with Dendrite
# 3. Summarizes collected information with OpenAI
#
# Uses OpenAI for natural language processing and Dendrite for browsing the web,
# enabling automated research on any topic using Reddit.

import json
from dendrite import Dendrite
from dotenv import load_dotenv
from urllib.parse import quote_plus
from openai import OpenAI
import re


load_dotenv()


# Simple function that uses OpenAI's API to generate a response to a prompt
def ai(prompt: str, output_json: bool = False):
    openai = OpenAI()
    if output_json:
        prompt += "\n\nYour output must be contain valid JSON wrapped in a json code block. E.g ```json\n[your output]\n```"
    messages = [{"role": "user", "content": prompt}]
    oai_res = openai.chat.completions.create(
        messages=messages,  # type: ignore
        model="gpt-4o",
    )
    message = oai_res.choices[0].message.content
    print("\n\n========= AI message =========\n", message, "\n================")
    if message:
        if output_json:
            # Find JSON content between ```json and ``` markers, or fall back to the entire content
            json_match = re.search(r"```json\s*(.*?)\s*```", message, re.DOTALL)
            content_to_parse = json_match.group(1) if json_match else message
            return json.loads(content_to_parse)
        return message
    raise Exception("Failed to get successful response from Open AI.")


# This function uses Dendrite to search for posts on reddit and summerize them based of a given topic
def search_and_summarize_reddit(topic_to_research: str):
    browser = Dendrite()

    # Generate search query from the user's topic
    search_query = ai(
        f"Generate a simple reddit search query for this research topic: '{topic_to_research}'"
        + "Output should be only be 1-3 keywords and nothing else. No quotes."
    )

    # Navigate to the search result page
    url = f"https://www.reddit.com/search/?q={quote_plus(search_query)}"
    browser.goto(url)

    # Extract search results
    search_data = browser.extract(
        "Get a list of dicts like so {subreddit: str, comment_amount: str, title: str, upvotes: str, url: str}"
    )

    # Get the urls of the posts that are related to the user's topic
    urls = ai(
        f"Output the urls for all posts relevant to as a list of strings: '{topic_to_research}'\n\nPosts: {search_data}",
        output_json=True,
    )

    # Extract the content from each post with Dendrite by opening several tabs
    posts = ""
    for url in urls:
        tab = browser.new_tab(url)
        post_data = tab.extract(
            "get the text content from the post and all the comments."
        )
        posts += f"\n\nPOST:\n{post_data}"
        print("post_data: ", post_data)
        tab.close()

    # Summarize the posts with OpenAI
    summary = ai(
        f"Based of these posts, please help the user with their research question: '{topic_to_research}' "
        + f"Here are the posts:\n{posts}"
    )

    return summary


# Uses Dendrite to search Reddit and summarize the results
summary = search_and_summarize_reddit(
    "What are people's opinions on CrewAI? Do people like it?"
)
