from typing import List
from dendrite import Dendrite


def search_linkedin(name: str) -> str:
    """This tool searches for a person on LinkedIn. It returns a few results that you can look through, and then inspect closer if you want."""
    with Dendrite(auth="linkedin.com") as client:
        client.goto("https://linkedin.com/")
        client.fill("the search bar", name)
        client.press("Enter")
        results = client.extract(
            "the search results as a list of strings containing info on each result, make sure you get the url of the profile as well",
            str,
        )
        return results


def open_linkedin_profile(urls: List[str]) -> str:
    """This tool opens a LinkedIn profile page."""
    with Dendrite(auth="linkedin.com") as client:
        profile_information = []
        for url in urls:
            page = client.new_tab(url)
            info = page.extract("all relevant profile information as a string")
            profile_information.append(info)

        return "\n".join(profile_information)
