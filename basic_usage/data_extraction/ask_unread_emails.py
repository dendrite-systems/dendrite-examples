from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

# Initiate Dendrite instance, read how to authenticate here: https://docs.dendrite.systems/concepts/authentication
client = Dendrite(auth="mail.google.com")

# Navigate and wait for loading
client.goto("https://mail.google.com/", expected_page="fully loaded email inbox")

# Ask agent about the state of the page, force it to return a boolean
# The difference between `ask` and `extract` is that `ask` will have an LLM look at the page everytime it's called,
# while `extract` will attempt to generate and re-run a pre-existing script.
has_new_emails = client.ask("Do I have any unread emails in my inbox?", type_spec=bool)

# Handle unread emails if there are any
if has_new_emails:
    print("There are unread emails in inbox")
else:
    print("No unread emails in inbox")
