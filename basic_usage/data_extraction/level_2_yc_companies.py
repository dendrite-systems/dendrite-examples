from dendrite import Dendrite
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


# Define Pydantic models
class Startup(BaseModel):
    name: str
    location: str
    description: str
    url: str


class Startups(BaseModel):
    items: list[Startup]


# Initiate Dendrite instance
browser = Dendrite()

# Navigate and interact with search field
browser.goto("https://www.ycombinator.com/companies")
browser.fill("Search field", value="AI agent")
browser.press("Enter")

# Extract startups with structured output with Pydantic model
startups = browser.extract("", Startups)

print(startups.items)
