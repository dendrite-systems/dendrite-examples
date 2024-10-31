[![Website](https://img.shields.io/badge/Website-dendrite.systems-blue?style=for-the-badge&logo=google-chrome)](https://dendrite.systems)
[![Documentation](https://img.shields.io/badge/Docs-docs.dendrite.systems-orange?style=for-the-badge&logo=bookstack)](https://docs.dendrite.systems)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/ETPBdXU3kx)

# Dendrite Python Examples

This repository has a wide variety of example code using Dendrite that you can try out of the box.

## Simple Dendrite Example 

```python
# Start the Dendrite browser
browser = Dendrite()

# Navigate to google
browser.goto("https://google.com")

try:
    browser.click("Reject all cookies")
except DendriteException:
    print("No reject all cookies button found")

# Google search "hello world"
browser.fill("Search input field", "hello world")
browser.press("Enter")

# Extract the search results as a list of dicts with url and title
results = browser.extract("The search results as a list of dicts with url and title")
print(results)
```

## Quickstart

Let's get started. First, we're going to install the required packages.

```
pip install -r requirements.txt
```

If you are using poetry, run the following:

```
poetry install
```

#### Installing the Web Driver

Now, lets install the web driver for running the Dendrite client locally. If you used pip to install the packages, run:

```
dendrite install
```

If you used Poetry, run:

```
poetry run dendrite install
```

#### Environment variables

Finally, we need to add our API keys. Copy the `.env.examples` file in the root directory and rename it to `.env`. Fill in your Dendrite API key, you can [get your API key here](https://dendrite.systems/app). Some examples use an Anthropic API key to run an agent, but the plain Dendrite examples don't require it.

## Try it Out!

Now you can simply run any python file in the repository! Feel free to experiment and modify the scripts. We recommend starting with `quickstart/hello_world.py`.

## Questions?

If you have any questions, check out our [documentation](https://docs.dendrite.systems) or get help in our [Discord](https://discord.gg/4rsPTYJpFb).
