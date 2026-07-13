from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def chatbot(state: State):
    return {
        "message": "Hello! You said: " + state["message"]
    }


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

result = graph.invoke({
    "message": "Hi LangGraph"
})

print(result)