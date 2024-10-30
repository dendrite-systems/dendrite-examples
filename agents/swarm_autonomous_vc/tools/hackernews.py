from langchain_core.tools import tool
from dendrite import AsyncDendrite


@tool
async def get_all_hackernews_posts() -> str:
    """Get's all the top posts from Hacker News from today"""
    async with AsyncDendrite() as client:
        await client.goto("https://news.ycombinator.com/")
        await client.wait_for("The front page is loaded")
        posts = await client.extract(
            "Get all top posts from Hacker News as a string containing title, url, points, and number of comments"
        )
        return posts


@tool
async def read_more_hackernews(url: str) -> str:
    """If you want to learn more about a Hacker News post, this call this function to go to it's url and summerize the contents."""
    async with AsyncDendrite() as client:
        await client.goto(url)
        info = await client.extract(
            "Get the informational text of the article/post/website, return as a string"
        )
        return info
