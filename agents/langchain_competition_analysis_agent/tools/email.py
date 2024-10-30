from dendrite import AsyncDendrite
from langchain_core.tools import tool


@tool
async def send_email(email_address: str, subject: str, body: str):
    """This tool sends an email to the provided email address with the provided subject and body. Don't use markdown in the body."""
    async with AsyncDendrite(auth="outlook.live.com") as client:
        await client.goto("https://outlook.live.com/mail/0/")
        await client.click("the new email button")
        await client.fill_fields(
            {"to_field": email_address, "subject_field": subject, "body_field": body}
        )
        await client.click("the send email button")
