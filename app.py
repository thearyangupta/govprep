import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from memory import ConversationMemory
from generate_v1 import answer

st.set_page_config(page_title="govprep", page_icon="study")
st.title("GOVPREP")
st.write("Ask about NCERT Polity, history, geography")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

st.subheader("Example questions")
example_questions = [
    "What are fundamental rights?",
    "What are the physical features of India?",
    "Who is the President of India?",
]
for example in example_questions:
    if st.button(example, key=f"example_{example}"):
        st.session_state.question_input = example

question = st.text_input("Your question:", key="question_input")
if question:
    try:
        with st.spinner("Thinking"):
            result = answer(question, st.session_state.memory)

        rewritten = result.get("rewritten")
        if rewritten and rewritten != question:
            st.caption(f"Searching for: {rewritten}")

        st.write(result["answer"])
        st.divider()

        with st.expander("Sources used"):
            for c in result.get("chunks", []):
                source_line = f"[{c.get('source')} p{c.get('page')}] {c.get('text', '')[:150]}"
                st.write(source_line)
    except Exception:
        st.error("Something went wrong. The model may be busy right now — please try again.")

with st.sidebar:
 st.header("govprep")
 st.write("AI study assistant for UPSC/CDS prep.")
 st.write("Sources: NCERT Polity, History, Geography")
 if st.button("Reset conversation"):
    st.session_state.memory = ConversationMemory()
    st.session_state.question_input = ""
    st.rerun