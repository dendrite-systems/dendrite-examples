import asyncio
import json
from typing import List

import streamlit as st
from dendrite import AsyncDendrite
from dendrite.exceptions import PageConditionNotMet
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from pathlib import Path

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool, BaseTool


load_dotenv(find_dotenv())


# Add this after imports
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
        json.dump(data, f, indent=2)  # Added indent for readable JSON


async def get_stargazers(star_gazers_url: str):
    fetched_users, all_star_gazers = load_cached_data()
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

    async def process_user(url, client: AsyncDendrite):
        async with semaphore:
            tab = await client.new_tab(url)
            try:
                await tab.wait_for(
                    "The entire profile to have loaded, including repositories if any, etc"
                )
            except PageConditionNotMet:
                print(f"Page condition not met for {url}, proceeding anyways")

            md = await tab.markdown()

            class StarGazer(BaseModel):
                full_name: str
                username: str
                bio: str
                location: str
                linkedin: str
                email: str
                twitter: str
                profile_pic_url: str
                summary_of_repos: str = Field(
                    description="Summerize what the star gazer has worked on and in what languages, also, emphasize cool things that they have worked on if available (and the urls of the repos), if not, let me know that the profile is pretty empty. Emphasize the any AI agent projects made in python or ts."
                )

            info = await tab.ask(
                f"Please get the requested information about the user, put n/a for unavailable information, here is some markdown from the page: {md}",
                StarGazer,
            )
            all_star_gazers[url] = info.dict()
            save_cached_data(all_star_gazers)
            await tab.close()

    async with AsyncDendrite(auth="github.com") as client:
        await client.goto(star_gazers_url)
        all_urls = await client.extract("Get the URLS of every star gazer")

        # Filter for new URLs and process them concurrently
        new_urls = [url for url in all_urls if url not in fetched_users]
        print(f"Processing new URLs: {new_urls}")
        await asyncio.gather(*[process_user(url, client) for url in new_urls])

    return all_star_gazers


asyncio.run(
    get_stargazers("https://github.com/dendrite-agent/dendrite-python-sdk/stargazers")
)

get_stargazers_tool = FunctionTool.from_defaults(async_fn=get_stargazers)

tools: List[BaseTool] = [
    get_stargazers_tool,
]

llm = OpenAI(model="gpt-4o")
agent = OpenAIAgent.from_tools(
    tools,
    llm=llm,
    verbose=True,
)


async def process_user_input(user_input, chat_history):
    res = await agent.achat(user_input, chat_history)
    return res


# Streamlit UI
def main():
    st.title("Competition Watch AI Agent")
    st.markdown(
        "Uses [LangChain](https://python.langchain.com/) for the AI agent and [Dendrite](https://dendrite.systems/) for the web interactions."
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like me to do?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            full_response = asyncio.run(
                process_user_input(prompt, st.session_state.messages)
            )
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
