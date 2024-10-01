import asyncio
from pydantic import BaseModel
from dendrite_sdk.async_api import AsyncDendrite
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


# Extract company info function
async def extract_info(client: "AsyncDendrite", url):
  # Open the URL in a new tab and extract company info
  page = await client.new_tab(url)
  company_info = await client.extract("The company info", type_spec=Company)

  # Close tab and return info
  await page.close()
  return company_info


# Main function (asynchronous)
async def main():
  # Initiate async Dendrite client
  client = AsyncDendrite()

  # Go to YC and search for AI agent companies
  await client.goto("https://ycombinator.com/companies")
  await client.fill("Search field", value="AI agent")

  # Extract the urls of the resulting list
  urls = await client.extract(
      "The URLs of each listed startup. Return this format: list[str]"
  )

  # Go to each URL concurrently in different tabs and extract company info
  tasks = [extract_info(client, url) for url in urls]
  companies = await asyncio.gather(*tasks)

  # Do something with the extracted company info
  print(companies)


asyncio.run(main())
