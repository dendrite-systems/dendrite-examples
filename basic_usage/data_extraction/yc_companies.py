from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

# Initiate Dendrite instance
client = Dendrite()

# Navigate and interact with search field
client.goto("https://www.ycombinator.com/companies")
client.fill("Search field", value="AI agent")
client.press("Enter")

# Extract startups with natural language description
startups = client.extract(
    "All companies. Return a list of dicts with name, location, description and url"
)

print(startups)
