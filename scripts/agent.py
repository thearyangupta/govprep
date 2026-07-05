from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv


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


tools = [search_corpus, calculate]

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

agent = create_react_agent(
    model=llm,
    tools=tools
)


if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                ("user", "What are Fundamental Rights? Also calculate 25 * 17.")
            ]
        }
    )

    print("\nFINAL ANSWER:")
    print(result["messages"][-1].content)