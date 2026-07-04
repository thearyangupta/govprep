from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def search_corpus(query: str) -> str:
    """Search NCERT books for relevant passages."""
    from retrieve_multi import retrieve

    chunks = retrieve(query, k=3)

    return "\n".join(
        f"[{c['source']} p{c['page']}] {c['text']}"
        for c in chunks
    )


def calculate(expression: str) -> str:
    """Evaluate a simple math expression."""
    try:
        return str(eval(expression))
    except Exception:
        return "could not calculate"


tools = [search_corpus, calculate]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

llm_with_tools = llm.bind_tools(tools)


def agent(state: State):
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"

    return END


graph_builder = StateGraph(State)

graph_builder.add_node("agent", agent)

tool_node = ToolNode(tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
)

graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What are Fundamental Rights? Also calculate 25 * 17."
                )
            ]
        }
    )

    print("\nFINAL ANSWER:")
    print(result["messages"][-1].content)