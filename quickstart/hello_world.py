from dendrite import Dendrite
from dendrite.exceptions import DendriteException
from dotenv import load_dotenv

load_dotenv()

# Initate the Dendrite client
browser = Dendrite()

# Navigate with the `goto` method
browser.goto("https://google.com")

try:
    browser.click("Reject all cookies")
except DendriteException:
    print("No reject all cookies button found")

# Populate the search field and press Enter key
browser.fill("Search input field", "hello world")
browser.press("Enter")

# Extract the search results as a list of dicts with url and title
results = browser.extract("The search results as a list of dicts with url and title")
print(results)
