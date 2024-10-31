from dendrite import Dendrite
from dotenv import load_dotenv

# Make sure you have a dendrite api key in your .env file
load_dotenv()


# Initate the Dendrite client
browser = Dendrite()

# You can also pass in a dendrite api key to the client if you prefer that
# browser = Dendrite(dendrite_api_key="your_api_key_here")

# Navigate to the page and wait for it to load
browser.goto("https://dendrite.systems")
browser.wait_for("the page to load")

# Get the page as markdown and print it
md = browser.markdown()
print(md)

print("=" * 200)

# Only get a certain part of the page as markdown
data_extraction_md = browser.markdown("the part about data extraction")
print(data_extraction_md)
