from dendrite_sdk import Dendrite
from dotenv import load_dotenv

load_dotenv()

def get_transactions() -> str:
    client = Dendrite(auth="mercury.com")

    # Navigate and wait for loading
    client.goto(
      "https://app.mercury.com/transactions",
      expected_page="Dashboard with transactions"
    )
    client.wait_for("The transactions to finish loading")

    # Modify filters
    client.click("The 'add filter' button")
    client.click("The 'show transactions for' dropdown")
    client.click("The 'this month' option")

    # Download file
    client.click("The 'export filtered' button")
    transactions = client.get_download()

    # Save file locally
    path = "files/transactions.xlsx"
    transactions.save_as(path)

    return path

def analyze_transactions(path: str):
    ...