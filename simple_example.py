import asyncio
import os
from dendrite_sdk import DendriteBrowser


async def google_search_videos(query: str):
    # You need to provide an Open AI key and an anthropic key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # Get your Dendrite API get from dendrite.se.
    dendrite_api_key = os.environ.get("DENDRITE_API_KEY", "")

    # Initate the Dendrite Browser
    browser = DendriteBrowser(
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        dendrite_api_key=dendrite_api_key,
    )

    # Navigate with goto. This returns a 'DendritePage' that represents the current page.
    page = await browser.goto("https://google.com")

    # Get elements from the current page with `get_elements`.
    search_bar = await page.get_element("The search bar")
    # Let's enter the search query into the search bar.
    await search_bar.fill(query)

    # Press enter to search
    await page.keyboard.press("Enter")

    await page.wait_for("the search results to load")

    # Get the video tab to see video results
    video_tab = await page.get_element("The tab for showing video results")
    # Click the video tab
    await video_tab.click()

    # Extract all the videos URLs
    data = await page.extract(
        "Get all the urls of the displayed videos as a list of valid urls as strings, return an exception if no videos are found"
    )
    urls = data.return_data
    print("urls: ", urls)
    for url in urls:
        print("url: ", url)


asyncio.run(google_search_videos("Polar bear"))
