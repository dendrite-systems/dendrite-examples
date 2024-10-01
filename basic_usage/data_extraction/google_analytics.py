from dendrite_sdk import Dendrite
from dotenv import load_dotenv

load_dotenv()

def get_visitor_count() -> int:
    client = Dendrite(auth="analytics.google.com")

    # Navigate with authenticated session
    client.goto(
        "https://analytics.google.com/analytics/web",
        expected_page="Google Analytics dashboard",
    )

    # Extract visitors as integer
    visitor_count = client.extract("The amount of visitors this month", int)
    return visitor_count
