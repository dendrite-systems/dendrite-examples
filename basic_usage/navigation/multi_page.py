from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

client = Dendrite()

# Open multiple URLs in new tabs
page1 = client.goto("https://www.example.com", new_page=True)
page2 = client.goto("https://www.anotherexample.com", new_page=True)

# Perform actions on page1
page1.click("Sign up button")
page1.fill("Email input", value="user@example.com")

# Perform actions on page2
page2.click("Contact us link")
page2.fill("Message textarea", value="Hello, I have a question.")
