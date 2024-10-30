import asyncio
import json

import streamlit as st
from dendrite import AsyncDendrite
from dendrite.exceptions import PageConditionNotMet
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Type

from openai import AsyncOpenAI


current_file_path = Path(__file__).resolve()
env_path = current_file_path.parent / ".env"
load_dotenv(env_path, override=True)


CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "stargazers_data.json"


def load_cached_data():
    CACHE_DIR.mkdir(exist_ok=True)
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return set(data.keys()), data
    return set(), {}


def save_cached_data(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


class GetStargazersTool:
    @staticmethod
    def get_function_schema():
        return {
            "type": "function",
            "function": {
                "name": "get_stargazers",
                "description": "Gets information about GitHub users who have starred a repository, even scores each candidate which is useful for deciding which is the best candidate.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "star_gazers_url": {
                            "type": "string",
                            "description": "The URL of the stargazers page for a GitHub repository",
                        }
                    },
                    "required": ["star_gazers_url"],
                },
            },
        }

    @staticmethod
    async def execute(star_gazers_url: str) -> str:
        fetched_users, all_star_gazers = load_cached_data()
        new_star_gazers = {}
        semaphore = asyncio.Semaphore(10)

        async def open_stargazer_in_tab(url, client: AsyncDendrite):
            async with semaphore:
                tab = await client.new_tab(url)
                try:
                    await tab.wait_for(
                        "The entire profile to have loaded, including repositories if any, etc. Usually only takes a few seconds."
                    )
                except PageConditionNotMet:
                    print(f"Page condition not met for {url}, proceeding anyways")

                md = await tab.markdown()

                class StarGazer(BaseModel):
                    full_name: str
                    username: str
                    bio: str
                    location: str
                    email: str
                    full_linkedin_url: str
                    full_twitter_url: str
                    personal_website_url: str
                    other_social_media: str
                    profile_pic_url: str
                    summary_of_repos: str = Field(
                        description=(
                            "Summerize what the star gazer has worked on and in what languages. "
                            "Emphasize cool things that they have worked on if available (and the urls of the repos), "
                            "if not, let me know that the profile is pretty empty. "
                            "Emphasize the any AI projects made in python or TS."
                        )
                    )
                    score: str = Field(
                        description=(
                            "Give a 'score' to the star gazer from 0 to 100 based on how promising they are. "
                            "A high score should be granted to candidates that have"
                            "worked on AI/llm projects (Web AI agents is best, but not required)"
                            "worked on projects in Python or TS"
                            "worked with web browser tools like Selenium, playwright"
                            "has experience working on open source projects. Do some reasoning here and then output the score."
                        )
                    )

                info = await tab.ask(
                    (
                        f"We are trying to find potential hires for a project and/or users to interview. "
                        f"Please get the requested information about the user, put n/a for unavailable information,"
                        f"here is some markdown from the page: {md}"
                    ),
                    StarGazer,
                )
                new_star_gazers[url] = info.model_dump()
                save_cached_data(all_star_gazers)
                await tab.close()

        async with AsyncDendrite(auth="github.com") as client:
            await client.goto(star_gazers_url)
            all_urls = await client.extract("Get the URLS of every star gazer")

            # Only look at new URLs that we haven't seen before and process them 10 at a time
            new_urls = [url for url in all_urls if url not in fetched_users]
            print(f"Processing new URLs: {new_urls}")
            await asyncio.gather(
                *[open_stargazer_in_tab(url, client) for url in new_urls]
            )
            print(f"Got these star gazers: {new_star_gazers}")

        return f"Got these star gazers: {new_star_gazers}"


class SendEmailTool:
    @staticmethod
    def get_function_schema():
        return {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": (
                    "Sends an email to a given email address. Ask for permission from the user first before you send an email though! Show them the email and the star gazer candidate first before sending so they can confirm."
                    """This is a great example of an email: Hi!\nI noticed that you starred the dendrite SDK on Github, thanks! :) I saw you've been working on web AI agents and data extraction, it would be really useful for me to hear your thoughts on the SDK, would you like to jump on a video call some time?\nIf so, just let me know!\nKind regards,\nDendrite Agent"""
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_address": {
                            "type": "string",
                            "description": "Email address to send to",
                        },
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"},
                    },
                    "required": ["email_address", "subject", "body"],
                },
            },
        }

    @staticmethod
    async def execute(email_address: str, subject: str, body: str) -> str:
        client = AsyncDendrite(auth="outlook.live.com")

        # Navigate and check for successful authentication
        await client.goto("https://outlook.live.com/mail/0/")

        # Create new email and populate fields
        await client.click("the new email btn")
        await client.fill("the_email_recipient_input", email_address)
        await client.press("Enter")
        await client.fill("the_email_subject_input", subject)
        await client.fill("the_email_body_input", body)

        # Send email
        await client.click("the send btn")

        return "Email sent successfully"


async def process_user_input(prompt, messages):
    client = AsyncOpenAI()

    current_messages = [
        {
            "role": "system",
            "content": (
                "Your job is to help me find promising hires/interviewees for the project 'Dendrite' which is a Python SDK for "
                "building tools for AI agents so they can browse the web. "
                "You can include markdown formatting in your responses. When showing user profiles, "
                "format them nicely with their profile picture (using ![name](url)) and other details in a structured way. "
                "Use markdown tables, headers, and other formatting to make the information easy to read. E.g:\n"
                "### John Doe\n"
                "![avatar](https://avatars.githubusercontent.com/u/12345)\n"
                "- **Location**: San Francisco\n"
                "- **Bio**: AI Engineer passionate about LLMs\n"
                "...\n\n"
                "To stop calling functions and ask the user a question, simply respond with a message without a function call."
            ),
        }
    ]

    # Add historical messages from the session state
    for msg in messages:
        current_messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the current prompt
    current_messages.append({"role": "user", "content": prompt})

    tools = [GetStargazersTool, SendEmailTool]
    function_schemas = [tool.get_function_schema() for tool in tools]

    while True:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=current_messages,  # type: ignore
            tools=function_schemas,
            tool_choice="auto",
        )
        message = response.choices[0].message

        # Add assistant's message to history
        current_messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": message.tool_calls,  # type: ignore
            }
        )

        # Stop if no function call
        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            tool_call_id = tool_call.id
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Find the matching tool and execute it
            for tool in tools:
                if tool.get_function_schema()["function"]["name"] == tool_name:
                    print(
                        f"Executing tool: {tool.get_function_schema()['function']['name']}"
                    )
                    result = await tool.execute(**tool_args)
                    current_messages.append(
                        {
                            "role": "tool",
                            "name": tool_name,
                            "content": str(result),
                            "tool_call_id": tool_call_id,
                        }
                    )
                    break


def main():
    # Initialize messages if they don't exist in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("GitHub Stargazers Analysis Agent")
    st.markdown(
        "Uses [OpenAI's SDK](https://github.com/openai/openai-python) for the AI agent and [Dendrite](https://dendrite.systems/) for the browser tools."
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Use unsafe_allow_html=True to render profile images and formatted content
            st.markdown(message["content"], unsafe_allow_html=True)

    # Replace text_input with chat_input
    if prompt := st.chat_input("What would you like me to do?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            full_response = asyncio.run(
                process_user_input(prompt, st.session_state.messages)
            )
            # Use unsafe_allow_html=True for the assistant's response
            message_placeholder.markdown(full_response, unsafe_allow_html=True)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
