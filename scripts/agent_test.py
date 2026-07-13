from google import genai
from google.genai import types
from llm import client


MAX_STEPS = 5


def search_corpus(query: str):
    """Search NCERT books for relevant passages."""
    from legacy.chromadb.retrieve_multi import retrieve

    chunks = retrieve(query, k=3, collection_name="govprep_v2")

    return "\n".join(
        f"[{c['source']} p{c['page']}] {c['text']}"
        for c in chunks
    )


def calculate(expression: str):
    """Evaluate a simple math expression."""
    try:
        return str(eval(expression))
    except Exception:
        return "could not calculate"


search_function = {
    "name": "search_corpus",
    "description": "Search NCERT books for relevant passages.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or topic to search in the NCERT corpus.",
            }
        },
        "required": ["query"],
    },
}


calculate_function = {
    "name": "calculate",
    "description": "Evaluate a simple math expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A simple math expression, for example 25 * 17.",
            }
        },
        "required": ["expression"],
    },
}


tools = [
    {
        "function_declarations": [
            search_function,
            calculate_function,
        ]
    }
]


def run_agent(question: str):
    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=question)
            ],
        )
    ]

    for step in range(MAX_STEPS):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config={
                "tools": tools,
            },
        )

        messages.append(response.candidates[0].content)

        part = response.candidates[0].content.parts[0]

        if part.function_call:
            function_call = part.function_call

            print("Tool requested:", function_call.name)
            print("Arguments:", function_call.args)

            if function_call.name == "search_corpus":
                tool_result = search_corpus(**function_call.args)

            elif function_call.name == "calculate":
                tool_result = calculate(**function_call.args)

            else:
                tool_result = "Unknown tool requested."

            messages.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={
                                "result": tool_result
                            },
                        )
                    ],
                )
            )

            continue

        return response.text

    return "Stopped after MAX_STEPS to prevent infinite loop."


if __name__ == "__main__":
    answer = run_agent(
        "What are fundamental rights? Also calculate 25 * 17."
    )

    print("\nFINAL ANSWER:")
    print(answer)