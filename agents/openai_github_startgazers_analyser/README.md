![Stargazers Demo](https://github.com/user-attachments/assets/2eeb3db5-fdc5-4b17-9f8f-d1a89d677183)


https://github.com/user-attachments/assets/bcaf857b-789d-4bfc-a420-4e5cb4a93162


***

This example repo contains an AI agent that can use the OpenAI SDK to analyze and reach out to GitHub stargazers using the [Dendrite Browser SDK](https://github.com/dendrite-systems/dendrite-python-sdk). The agent can identify potential candidates for hiring or user interviews based on their GitHub profiles and repositories.

<br /><br />
## Overview/Features
Repo contains:
- OpenAI Tools Agent
- Streamlit UI
- Tool to analyze GitHub stargazers:
  - Profile information extraction
  - Repository analysis
  - Candidate scoring
- Tool to send outreach emails via Outlook

<br /><br />
## Prerequisites

To run this yourself locally, you'll need the following:

- Python v. 3.9+
- An OpenAI API key
- A free [Dendrite API key](https://dendrite.systems/create-account)
- The [Dendrite Vault Chrome Extension](https://chromewebstore.google.com/detail/dendrite-vault/faflkoombjlhkgieldilpijjnblgabnn) if you want to authenticate your agent to use your email.

Pro tip:
- [Install Poetry package manager](https://python-poetry.org/)

<br /><br />
## Dendrite Example Snippet

Here's how easy it is to analyze GitHub stargazers with Dendrite:

```python
async def get_stargazers(star_gazers_url: str) -> str:
    """Gets information about GitHub users who have starred a repository"""
    async with AsyncDendrite(auth="github.com") as client: # Authenticate with github
        await client.goto(star_gazers_url) # Navigate to the stargazers page
        all_urls = await client.extract("Get the URLS of every star gazer")
        
        for url in all_urls:
            tab = await client.new_tab(url)
            profile_info = await tab.markdown()
            # Process profile information...
            await tab.close()
```

<br /><br />
## Getting Started

1. **Download this repo:**

    ```bash
    git clone https://github.com/dendrite-systems/langchain-dendrite-example.git
    ```
    ```bash
    cd langchain-dendrite-example
    ```

2. **Install packages** – Don't forget `dendrite install` since this installs the browser binaries

    ```bash
    # with poetry
    poetry install && poetry run dendrite install
    ```
    
    ```bash
    # with pip
    pip install -r requirements.txt && dendrite install
    ```

3. **Create a `.env` file** – Get a free Dendrite API key [here](https://dendrite.systems/create-account).

    ```
    OPENAI_API_KEY=sk-Cs...
    DENDRITE_API_KEY=sk_4b0...
    ```

4. **Run the project:**
    
    ```bash
    # with poetry
    poetry run streamlit run stargazer_agent.py
    ```
    ```bash
    # with pip
    streamlit run stargazer_agent.py
    ```

5. **Try it out**, try sending the message:
   ```bash
   Hi, please analyze the stargazers for https://github.com/your-repo and find promising candidates for interviews.
   ```

   The agent will use the correct tool to get the stargazers.

   To send outreach emails, your agent needs to be authorized to use your Outlook account first. Here's how:
   
   1. Install the [Dendrite Vault Chrome Extension](https://chromewebstore.google.com/detail/dendrite-vault/faflkoombjlhkgieldilpijjnblgabnn)
   2. Log into Outlook in your own browser
   3. Open the Dendrite vault extension
   4. Press "Authenticate on outlook.com"

   You can then try:
   
   ```bash
   Hi, please analyze the stargazers for https://github.com/your-repo and draft outreach emails for the most promising candidates. Show them to me and I'll tell you who to reach out to.
   ```

<br /><br />
## Why is Dendrite so slow the first time I run a tool, and then so fast?

It's because the first time you call `client.extract("get all the stargazer urls")` our coding agents need to generate a script to fetch the products from the HTML.

The next time you call the same prompt (and the website structure hasn't changed), the same script will be re-used – instantly returning the data.

<br /><br />
## Contributing

Have any cool ideas for features/improvements, create a pull request – contribution is warmly welcome! :)

<br /><br />
## Support

If you have any questions or need help, please join the [Dendrite Discord](https://discord.gg/4rsPTYJpFb)
