from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

# Initate the Dendrite client
client = Dendrite()

# Navigate with the `goto` method
client.goto("https://google.com")

# Populate the search field and press Enter key
client.fill("Search input field", "hello world")
client.press("Enter")

