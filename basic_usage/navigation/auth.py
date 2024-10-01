from dendrite_sdk import Dendrite
from dendrite_sdk.exceptions import DendriteException
from dotenv import load_dotenv

load_dotenv()

# Initiate client with authenticated session
client = Dendrite(auth="mail.google.com")

# Go to website with authenticated session
try:
    client.goto("https://mail.google.com/", expected_page="Gmail inbox")
except DendriteException as e:
    print("Authentication failed, page was not a Gmail inbox")
