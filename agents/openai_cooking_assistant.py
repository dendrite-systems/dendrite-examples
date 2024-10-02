# Cooking assistant agent using OpenAI's GPT and Dendrite SDK:
# 1. Take in a recipe request and dietary preferences
# 2. Searches ICA's website for relevant recipes with Dendrite
# 3. Selects the best recipe based on preferences using OpenAI
# 4. Extracts and translates the chosen recipe
#
# Uses OpenAI for the assistant and Dendrite for browsing the web,
# enabling automated recipe finding and selection based on user preferences.


import asyncio
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from dendrite_sdk import AsyncDendrite


def ai_request(prompt: str):
    openai = OpenAI()
    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]
    oai_res = openai.chat.completions.create(messages=messages, model="gpt-4o")
    if oai_res.choices[0].message.content:
        return oai_res.choices[0].message.content
    raise Exception("Failed to get successful response from Open AI.")


async def find_recipe(recipe: str, preferences: str):
    client = AsyncDendrite()
    await client.goto("https://www.ica.se/recept/")

    close_cookies_button = await client.get_element("The reject cookies button")
    if close_cookies_button:
        await close_cookies_button.click()

    await client.fill(
        "The search bar for searching recipes with placeholder sök ingrediens etc",
        recipe,
    )
    await client.press("Enter")

    recipes_res = await client.extract(
        "Get all the recipes on the page like this {{name: str, time_to_make: str, url_to_recipe: str}}"
    )

    find_recipe_prompt = f"""Here are some recipes:
    
    {recipes_res}
    
    Please output the url of the recipe that best suits these food preferences: {preferences}. 
    
    Important: You output should consist of only one valid URL, nothing else, pick the one that best suits my preferences."""

    url = ai_request(find_recipe_prompt)
    await client.goto(url)
    recipe = await client.extract(
        "Please output a nice, readable string containing the page's recipe that contains a header for ingredients and one for the steps in English.",
        str,
    )

    return recipe


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
        user_input = input(
            "What would you like to make? E.g 'Vegetarian tacos that can be made in 30 mins'\n\nYou: "
        )
        if user_input.lower() == "exit":
            break
        response = await agent.chat(user_input)
        print("Agent:", response)


if __name__ == "__main__":
    asyncio.run(main())
