import json
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from swarm import Agent, Swarm
from swarm.core import Result

from tools.linkedin import open_linkedin_profile, search_linkedin
from tools.producthunt import get_all_product_hunt_posts, get_product_hunt_creator_info

env_path = find_dotenv()
load_dotenv(env_path)


organisational_values = """Rules:
- Every time you write a message, start it with which agent you are.
- When investing, do it autonomously from start to finish. This could mean dicussing internally many times before making a decision. The general partner agent will make a final decision and report back to the user.
– Always write a message before calling a function.
- Delegate to one agent at a time.
"""


def send_message_to_sourcing_agent():
    """
    This function is used to send a message to the sourcing agent. Can be used to delegate a task or ask a question.
    """
    return sourcing_agent


def send_message_to_operations_agent():
    """
    This function is used to send a message to the operations agent. Can be used to delegate a task or ask a question.
    """
    return operations_agent


def report_back_to_general_partner_agent():
    """
    This function is used to report back to the general partner agent or to ask a question.
    """
    return general_partner_agent


general_partner_agent = Agent(
    model="gpt-4o",
    name="General Partner Agent",
    instructions="You are the General Partner Agent. Your job is to communicate with the Managing Partner (the user) and delegates tasks to the other agents."
    + organisational_values,
    functions=[
        send_message_to_sourcing_agent,
        send_message_to_operations_agent,
    ],
)


sourcing_agent = Agent(
    model="gpt-4o",
    name="Sourcing Agent",
    instructions="This agent finds fresh deals by searching the web for new startups. It also summerises it's finiding and returns them to the General Partner Agent so that they can make a decision if it's a good investment or not. They might have follow up questions. This agent researches products by going to product hunt and inspecting promising posts, it goes into the best posts and tries to find the full name of the creator, if it can find them, it will go to linkedin and inspect the profile of the creator. If it finds the creators it can open their linkedin profile and inspect it further."
    + organisational_values,
    functions=[
        get_all_product_hunt_posts,
        get_product_hunt_creator_info,
        report_back_to_general_partner_agent,
        search_linkedin,
        open_linkedin_profile,
    ],
)


def add_startup_to_portfolio():
    """
    This function is used to add a startup to the portfolio.
    """
    return "Startup added to portfolio"


operations_agent = Agent(
    model="gpt-4o",
    name="Operations Agent",
    instructions="This agent manages the portfolio, one a good startup is found, this agent is responsible for adding it to the portfolio. "
    + organisational_values,
    functions=[
        add_startup_to_portfolio,
        report_back_to_general_partner_agent,
    ],
)


def pretty_print_messages(messages) -> None:
    for message in messages:
        if message["role"] != "assistant":
            continue

        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    client = Swarm()
    print("Starting Swarm CLI 🐝")

    messages = []
    agent = starting_agent

    # while True:
    user_input = "start investing"  # input("\033[90mUser\033[0m: ")
    messages.append({"role": "user", "content": user_input})

    response = client.run(
        agent=general_partner_agent,
        messages=messages,
        context_variables={},
        debug=True,
    )

    pretty_print_messages(response.messages)

    messages.extend(response.messages)
    agent = response.agent


if __name__ == "__main__":
    run_demo_loop(general_partner_agent)


# Streamlit UI
def main():
    st.title("Autonomous VC Firm AI Agent")
    st.markdown(
        "Uses [Swarms](https://github.com/swarms-ai/swarms) for AI agents, [Streamlit](https://streamlit.io/) for the UI and [Dendrite](https://dendrite.systems) for the web tools."
    )

    client = Swarm()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = general_partner_agent

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like me to do?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            last_sender = ""
            response = client.run(
                agent=st.session_state.agent,
                messages=st.session_state.messages,
                context_variables={},
                stream=True,
                debug=False,
            )

            content = ""
            last_sender = ""

            for chunk in response:
                if "sender" in chunk:
                    last_sender = chunk["sender"]

                if "content" in chunk and chunk["content"] is not None:
                    if not content and last_sender:
                        print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                        last_sender = ""
                    # print(chunk["content"], end="", flush=True)
                    content += chunk["content"]

                if "tool_calls" in chunk and chunk["tool_calls"] is not None:
                    for tool_call in chunk["tool_calls"]:
                        f = tool_call["function"]
                        name = f["name"]
                        if not name:
                            continue
                        # print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

                if "delim" in chunk and chunk["delim"] == "end" and content:
                    print("END")  # End of response message
                    content = ""

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
