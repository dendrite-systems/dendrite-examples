import asyncio
import os
import time
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from dendrite_sdk import DendriteBrowser


def ai_request(prompt: str):
    openai = OpenAI()
    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]
    oai_res = openai.chat.completions.create(messages=messages, model="gpt-4o-mini")
    if oai_res.choices[0].message.content:
        return oai_res.choices[0].message.content
    raise Exception("Failed to get successful response from Open AI.")


async def find_recipe(recipe: str, preferences: str):
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    dendrite_api_key = os.environ.get("DENDRITE_API_KEY", "")

    start_time = time.time()
    dendrite = DendriteBrowser(
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        dendrite_api_key=dendrite_api_key,
    )
    page = await dendrite.goto("https://www.ica.se/recept/")

    close_cookies_button = await page.get_element(
        "The reject cookies button", use_cache=False
    )
    if close_cookies_button:
        print("close_cookies_button: ", close_cookies_button.locator)
        await close_cookies_button.click()

    search_bar = await page.get_element(
        "The search bar for searching recipes with placeholder sök ingrediens etc",
        use_cache=False,
    )
    await search_bar.fill(recipe)
    await page.keyboard.press("Enter")

    await page.wait_for("Wait for the recipies to be loaded")
    await page.scroll_to_bottom()
    recipes_res = await page.extract(
        "Get all the recipes on the page and return and array of dicts like this {{name: str, time_to_make: str, url_to_recipe: str}}"
    )

    print("recipes_res.return_data: ", recipes_res.return_data)

    find_recipe_prompt = f"""Here are some recipes:
    
    {recipes_res.return_data}
    
    Please output the url of the recipe that best suits these food preferences: {preferences}. 
    
    Important: You output should consist of only one valid URL, nothing else, pick the one that best suits my preferences."""

    url = ai_request(find_recipe_prompt)
    page = await dendrite.goto(url)
    res = await page.ask(
        "Please output a nice, readable string containing the page's recipe that contains a header for ingredients and one for the steps in English.",
        str,
    )

    generated_recipe = res.return_data
    print(
        f"Find recipe took: {time.time() - start_time}. Here is the recipe:\n\n{generated_recipe}"
    )
    await dendrite.close()
    return generated_recipe


class CookingAgent:
    def __init__(self):
        self.openai = OpenAI()

    async def chat(self, user_input: str):
        messages = [
            {
                "role": "system",
                "content": "You are a helpful cooking assistant. You can find recipes based on user preferences and dietary restrictions.",
            },
            {"role": "user", "content": user_input},
        ]

        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,  # type: ignore
            functions=[
                {
                    "name": "find_recipe",
                    "description": "Find a recipe based on the user's preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipe": {
                                "type": "string",
                                "description": "The type of recipe to search for",
                            },
                            "preferences": {
                                "type": "string",
                                "description": "User's dietary preferences and restrictions. If you don't know the user's preferences, ask them for them.",
                            },
                        },
                        "required": ["recipe", "preferences"],
                    },
                }
            ],
            function_call="auto",
        )

        message = response.choices[0].message

        if message.function_call:
            function_name = message.function_call.name
            function_args = eval(message.function_call.arguments)

            if function_name == "find_recipe":
                recipe = await find_recipe(
                    function_args["recipe"], function_args["preferences"]
                )
                return f"Here's a recipe that matches your preferences:\n\n{recipe}"

        return message.content


# Example usage
async def main():
    agent = CookingAgent()
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = await agent.chat(user_input)
        print("Agent:", response)


if __name__ == "__main__":
    asyncio.run(main())
