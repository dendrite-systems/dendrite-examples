from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()


# Initiate the Dendrite browser autenticated on outlook.live.com.
# Read how create authentication sessions here: https://docs.dendrite.systems/concepts/authentication
browser = Dendrite(auth="outlook.live.com")

# Navigate and check for successful authentication
browser.goto("https://outlook.live.com/mail/0/")

# Create new email and populate fields
browser.click("The new email button")
browser.fill("Recipient", "test@dendrite.systems")
browser.press("Enter")
browser.fill_fields({"Subject": "mock", "Message": "mock"})

input("Are you ready to send the email?")
# Send email
browser.click("The send button")
browser.close()
