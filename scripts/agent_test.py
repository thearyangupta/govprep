from google import genai
from llm import client


def search_corpus(query: str) -> str:
    """Search NCERT books for relevant passages."""
    from retrieve_multi import retrieve

    chunks = retrieve(query, k=3, collection_name="govprep_v2")

    return "\n".join(
        f"[{c['source']} p{c['page']}] {c['text']}"
        for c in chunks
    )


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


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are fundamental rights?",
    config={
        "tools": [{"function_declarations": [search_function]}],
    },
)

print(response)

function_call = response.candidates[0].content.parts[0].function_call

print("Function name:", function_call.name)
print("Arguments:", function_call.args)

tool_result = search_corpus(**function_call.args)

print("\nTool result:")
print(tool_result)