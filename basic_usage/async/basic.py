import asyncio
from dendrite.async_api import AsyncDendrite
from dotenv import load_dotenv

load_dotenv()


async def main():
    # Initiate async Dendrite client
    client = AsyncDendrite()

    # Navigate to page click on the described button
    await client.goto("https://example.com")
    await client.click("The button for getting started")


asyncio.run(main())
