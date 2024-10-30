import asyncio
from dendrite import Dendrite


def get_all_product_hunt_posts() -> str:
    """Get's all the posts from product hunt from today"""
    with Dendrite() as client:
        client.goto(f"https://www.producthunt.com/")
        client.click("the see all of today's posts button")
        print("HAH")
        posts = client.extract(
            "Get all today's posts from product hunt as a string containing name, desc, categories, upvotes and url",
            str,
        )
        return posts


def get_product_hunt_creator_info(url: str) -> str:
    """Call this tool to get the full name of the creator of the product on product hunt"""
    with Dendrite() as client:
        client.goto(url)
        info = client.ask(
            "We are trying to find out more about the creator of this product. Is the full name of the maker listed? If so, return it, otherwise return 'unknown'",
            str,
        )
        return info
