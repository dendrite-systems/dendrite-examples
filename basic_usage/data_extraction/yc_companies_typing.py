from dendrite_sdk import Dendrite
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
client = Dendrite()

# Navigate and interact with search field
client.goto("https://www.ycombinator.com/companies")
client.fill("Search field", value="AI agent")
client.press("Enter")

# Extract startups with structured output with Pydantic model
startups = client.extract("", Startups)

print(startups.items)

