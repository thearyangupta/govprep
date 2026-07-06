from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
load_dotenv()


@tool
def search_corpus(query: str) -> str:
    """Search GovPrep NCERT corpus for relevant passages."""
    from retrieve_multi import retrieve

    chunks = retrieve(query, k=3)

    if not chunks:
        return "No relevant passages found."

    return "\n".join(
        f"[{c['source']} p{c['page']}] {c['text']}"
        for c in chunks
    )


@tool
def calculate(expression: str) -> str:
    """Evaluate a simple math expression."""
    try:
        return str(eval(expression))
    except Exception:
        return "could not calculate"


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

tools = [search_corpus, calculate]

agent = create_react_agent(model, tools)

response = agent.invoke(
    {
        "messages": [
            (
                "user",
                "Compare fundamental rights and directive principles.",
            )
        ]
    },
    config={
        "recursion_limit":5
    }
)

for message in response["messages"]:
    print(message)