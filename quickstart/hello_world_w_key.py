from dendrite_sdk import Dendrite

# Get your Dendrite API key from dendrite.systems
DENDRITE_API_KEY = "..."

# Initate the Dendrite client
client = Dendrite(dendrite_api_key=DENDRITE_API_KEY)

# Navigate with the `goto` method
client.goto("https://google.com")

# Populate the search field and press Enter key
client.fill("Search input field", "hello world")
client.press("Enter")
