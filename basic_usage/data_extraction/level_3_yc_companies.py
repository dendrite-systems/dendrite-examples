import asyncio
from pydantic import BaseModel
from dendrite import AsyncDendrite
from dotenv import load_dotenv

load_dotenv()


# Define Pydantic Models for data extraction
class Founder(BaseModel):
    name: str
    linkedin: str | None
    twitter: str | None


class Company(BaseModel):
    name: str
    team_size: int
    location: str
    website_url: str
    founders: list[Founder]


# Extract company info from tab
async def extract_info(browser: "AsyncDendrite", url):
    # Open the URL in a new tab and extract company info
    tab = await browser.new_tab(url)
    company_info = await tab.extract("The company info ", type_spec=Company)

    # Close tab and return info
    await tab.close()
    return company_info


# Main function (asynchronous)
async def main():
    # Initiate async Dendrite browser
    browser = AsyncDendrite()

    # Create semaphore to limit the amount of visited page at a time to 10
    semaphore = asyncio.Semaphore(10)

    async def bounded_extract(url):
        async with semaphore:
            return await extract_info(browser, url)

    # Go to YC and search for AI agent companies
    await browser.goto("https://ycombinator.com/companies")
    await browser.fill("Search field", value="AI agent")

    # Extract the urls of the resulting list
    urls = await browser.extract(
        "The URLs of each listed startup. Return this format: list[str]"
    )

    # Go to each URL concurrently in different tabs and extract company info
    # Now using bounded_extract instead of extract_info directly
    tasks = [bounded_extract(url) for url in urls]
    companies = await asyncio.gather(*tasks)

    # Do something with the extracted company info
    print(companies)


asyncio.run(main())
