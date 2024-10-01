from dendrite_sdk import Dendrite
from dotenv import load_dotenv

load_dotenv()

# Initiate Dendrite instance
client = Dendrite(auth="mail.google.com")

# Navigate and wait for loading
client.goto("https://mail.google.com/", expected_page="Email inbox")

# Ask agent about the state of the page
has_new_emails = client.ask(
    "Do I have any unread emails in my inbox?", type_spec=bool
)

# Handle unread emails if there are any
if has_new_emails:
  print("There are unread emails in inbox")
else:
  print("No unread emails in inbox")
