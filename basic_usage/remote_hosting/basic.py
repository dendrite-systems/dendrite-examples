# from dendrite_sdk import Dendrite
from dendrite_sdk.sync_api.ext.browserbase import BrowserbaseBrowser

...

# client = Dendrite(...)
client = BrowserbaseBrowser(
    # Use interchangeably with the Dendrite class
    browserbase_api_key="...", # or specify the browsebase keys in the .env file
    browserbase_project_id="..."
)

...