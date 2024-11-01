from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()


def get_visitor_count() -> int:
    # read how create authentication sessions here: https://docs.dendrite.systems/concepts/authentication
    browser = Dendrite(auth="analytics.google.com")

    # Navigate with authenticated session
    browser.goto(
        "https://analytics.google.com/analytics/web",
        expected_page="Google Analytics dashboard",
    )

    # Extract visitors as integer
    visitor_count = browser.extract("The amount of visitors this month", int)
    return visitor_count
