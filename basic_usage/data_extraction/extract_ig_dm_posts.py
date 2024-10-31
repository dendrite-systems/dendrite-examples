from dendrite import Dendrite
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


# Initiate Dendrite instance, read how create authentication sessions here: https://docs.dendrite.systems/concepts/authentication
browser = Dendrite(auth=["instagram.com"])

# Navigate to latest conversation
browser.goto(
    "https://www.instagram.com/direct/inbox/", expected_page="Instagram DM inbox"
)
browser.click("Conversation at the top of the the sidebar")

# Get shared posts
posts = browser.extract(
    "Extract the posts sent to me from another user", type_spec=Posts
)

print(posts.items)
