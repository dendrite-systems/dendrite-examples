from dendrite_sdk import Dendrite
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Define Pydantic models
class Post(BaseModel):
  title: str
  url: str
  date_sent: str

class Posts(BaseModel):
  items: list[Post]

# Initiate Dendrite instance
client = Dendrite(auth=["instagram.com"])

# Navigate to latest conversation
client.goto(
  "https://www.instagram.com/direct/inbox/",
  expected_page="Instagram DM inbox"
)
client.click("Conversation at the top of the the sidebar")

# Get shared posts
posts = client.ask(
  "Extract the posts sent to me from another user",
  type_spec= Posts
)

print(posts.items)
