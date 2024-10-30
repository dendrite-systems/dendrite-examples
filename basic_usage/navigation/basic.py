from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

# Initialize Dendrite instance
client = Dendrite()

# Navigate to a website
client.goto("https://www.example.com")
