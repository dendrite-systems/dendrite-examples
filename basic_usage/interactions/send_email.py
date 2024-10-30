from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

def send_email(to, subject, message):
    client = Dendrite(auth="outlook.live.com")

    # Navigate and check for successful authentication
    client.goto(
        "https://outlook.live.com/mail/0/",
        expected_page="An email inbox"
    )

    # Create new email and populate fields
    client.click("The new email button")
    client.fill_fields({
        "Recipient": to,
        "Subject": subject,
        "Message": message
    })

    # Send email
    client.click("The send button")