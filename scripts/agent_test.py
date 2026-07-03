from google import genai
from llm import client


def get_weather(city: str) -> str:
    """Fake weather function."""
    return f"The weather in {city} is 28C and sunny."


weather_function = {
    "name": "get_weather",
    "description": "Get the weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name, for example Delhi",
            }
        },
        "required": ["city"],
    },
}


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the weather in Delhi?",
    config={
        "tools": [{"function_declarations": [weather_function]}],
    },
)

print(response)