from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

load_dotenv()


@tool
def search_corpus(query: str) -> str:
    """
    Search the GovPrep NCERT corpus for information related to UPSC/CDS.
    Use this tool whenever the user asks factual questions that require
    retrieving information from the study material.
    """
    from retrieve_multi import retrieve

    try:
        chunks = retrieve(query, k=3)

        if not chunks:
            return "No relevant passages found in the GovPrep knowledge base."

        return "\n".join(
            f"[{c['source']} p{c['page']}] {c['text']}"
            for c in chunks
        )

    except Exception as e:
        return f"Tool error: {e}. Try a different approach."


@tool
def calculate(expression: str) -> str:
    """
    Evaluate mathematical expressions.
    Use this tool whenever the user asks arithmetic or numerical questions.
    """
    try:
        return str(eval(expression))

    except Exception as e:
        return f"Tool error: {e}. Try a different approach."


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

tools = [search_corpus, calculate]

agent = create_react_agent(
    model=model,
    tools=tools
)

response = agent.invoke(
    {
        "messages": [
            (
                "user",
                "What is (25 * 18) + 120?"
            )
        ]
    },
    config={
        "recursion_limit": 15
    }
)

print("=" * 60)
print("REASONING TRACE")
print("=" * 60)

for message in response["messages"]:
    print(f"\n[{message.type.upper()}]")
    print(message.content)