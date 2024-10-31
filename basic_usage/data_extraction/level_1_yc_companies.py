from dendrite import Dendrite
from dotenv import load_dotenv
import pprint

load_dotenv()

# Initiate Dendrite instance
browser = Dendrite()

# Navigate and interact with search field
browser.goto("https://www.ycombinator.com/companies")
browser.fill("Search field", value="AI agent")  # Element selector cached since before
browser.press("Enter")

# Extract startups with natural language description
# Once created by our agent, the same script will be cached and reused
startups = browser.extract(
    "All companies. Return a list of dicts with name, location, description and url"
)
pprint.pprint(startups, indent=2)
