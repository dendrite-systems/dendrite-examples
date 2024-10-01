import time
from datetime import datetime
import os
from typing import List, Literal

from dendrite_sdk import Dendrite

from dotenv import load_dotenv
from pydantic import BaseModel
import requests

from langchain.tools import tool

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv

load_dotenv()


class Message(BaseModel):
    sender: Literal["me", "other"]
    text: str
    date: str


class Chat(BaseModel):
    messages: List[Message]


class InstagramTools:
    def __init__(self):
        self.client = Dendrite(auth="instagram.com")

    def goto_chat(self, chat_name: str):
        client = self.client

        # Go to Instagram DM inbox and press button to open a chat
        client.goto("https://www.instagram.com/direct/inbox/")
        client.click("Icon button that creates a new chat")

        # Fill chat name in search field and wait for loading to complete
        client.fill("Input for which user to send the message to", chat_name)
        time.sleep(3)

        # Select top item and press button to open chat
        client.press("Tab")
        client.press("Enter")
        client.click("Button to open/start a chat in the 'send message' modal")

    def send_message_in_chat(self, message: str, chat_name: str):
        client = self.client

        # Open chat
        try:
            self.goto_chat(chat_name)
        except RuntimeError as e:
            return str(e)

        # Enter message and send
        client.fill("The input where the user writes new messages", message)
        client.press("Enter")

        return f"Message sent in chat with {chat_name}: '{message}'"

    def get_messages_from_chat(self, chat_name: str):
        client = self.client

        # Open chat
        try:
            self.goto_chat(chat_name)
        except RuntimeError as e:
            return str(e)

        # Extract messages
        chat: Chat = client.extract(
            "The latest text messages in the current conversation. Skip any type of shared content.",
            type_spec=Chat,
        )

        return chat.messages

    def post_content(self, text: str, image_path: str):
        client = self.client

        # Go to Instagram and click button for creating a post
        client.goto("https://www.instagram.com/")
        client.wait_for("Loading to finish")
        client.click(
            "Button in side bar menu that creates a new post",
            expected_outcome="A modal for creating a new post should appear",
        )

        # Upload image
        client.click(
            "Button in the 'Create new post' modal for selecting upload content from the computer"
        )
        client.upload_files(image_path)
        client.wait_for(
            "Image to be added to the modal and the crop interface to appear"
        )

        # Press next until caption input field appears
        next_btn = client.get_element("Next step button in modal")
        next_btn.click(expected_outcome="Side bar with filters appears")
        next_btn.click(expected_outcome="Side bar with a caption input field appears")

        # Fill in caption
        client.fill("Caption input field for the new post", text)

        client.click("The button for sharing the new post")
        client.wait_for("Success modal that indicates that the post has been shared")

        return f"Image has been posted with caption: {text}"


def main():
    global config

    # Get Instagram Tools
    ig_tools = InstagramTools()

    # Util function for generating config for agent
    generate_config = lambda thread_id=None: {
        "configurable": {
            "thread_id": thread_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        }
    }

    # Create tools for agent
    @tool
    def get_messages(user_name: str):
        """Get latest instagram messages from a chat with a specific user based on their username"""
        return ig_tools.get_messages_from_chat(user_name)

    @tool
    def send_message(message: str, user_name: str):
        """Send a direct Instagram message to a specific user based on their username.
        IMPORTANT: Only use this tool after explicitly asking the user for the message content and receiving their approval.
        """
        return ig_tools.send_message_in_chat(message, user_name)

    @tool
    def upload_post(caption: str, image_url: str):
        """Upload a post to the user's Instagram account."""

        image_path = download_image(image_url)

        return ig_tools.post_content(caption, image_path)

    @tool
    def generate_image(prompt: str):
        """Generate an image from a prompt and return the URL to the user.
        IMPORTANT: If the prompt from the user is not very descriptive, write a new, more detailed prompt based on the user input that you use to invoke this tool.
        """

        url = DallEAPIWrapper(model="dall-e-3").run(prompt)

        return url

    # Util function for saving image locally from url
    def download_image(url):
        directory = "test/saved_images"
        os.makedirs(directory, exist_ok=True)

        response = requests.get(url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"

        print("Response code for image: ", response.status_code)

        if response.status_code == 200:
            filepath = os.path.join(directory, filename)

            with open(filepath, "wb") as file:
                file.write(response.content)

            return filepath
        else:
            raise RuntimeError("Failed to download image")

    # Create the agent with Memory, Model, System Prompt and Tools
    memory = MemorySaver()
    model = ChatAnthropic(model_name="claude-3-sonnet-20240229")
    system_prompt = SystemMessage(
        content="""You are a helpful AI Agent called 'Igor the AI Agent' developed by Dendrite that is specialized in doing Instagram actions on behalf of the user.
    You have been provided tools to do this reliably.
    """
    )
    tools = [
        get_messages,
        send_message,
        generate_image,
        upload_post,
    ]

    # Initiate ReAct Agent
    agent_executor = create_react_agent(
        model,
        tools,
        checkpointer=memory,
        state_modifier=system_prompt,
    )

    # Utils
    config = generate_config()
    separator = "-------"

    # Create chat loop between Human and Agent in console
    while True:

        # Get human message input
        user_input = input("User: ")
        print(separator)
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Add new human message to agent and print response
        res = agent_executor.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config
        )
        latest_message = res["messages"][-1].content

        print(latest_message)
        print(separator)


main()
