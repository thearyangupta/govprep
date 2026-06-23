import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from memory import ConversationMemory
from generate_v1 import answer

st.set_page_config(page_title="GovPrep AI", page_icon="study", layout="wide")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

with st.sidebar:
    st.title("GovPrep AI")
    st.write("AI study assistant for UPSC/CDS prep.")
    st.write("Sources: NCERT Polity, History, Geography")
    st.divider()
    if st.button("Reset conversation"):
        st.session_state.memory = ConversationMemory()
        st.session_state.question_input = ""
        st.experimental_rerun()

st.markdown("# GovPrep AI")
st.markdown("#### NCERT Doubt Solver")
st.write("Ask about NCERT Polity, History, and Geography.")

st.markdown("### Try asking:")
col1, col2, col3 = st.columns(3)
examples = [
    "What is Article 21?",
    "Causes of 1857 Revolt?",
    "Atmospheric layers?",
]
for col, example in zip((col1, col2, col3), examples):
    if col.button(example, key=f"example_{example}"):
        st.session_state.question_input = example

question = st.text_input("Your question:", key="question_input")
if question:
    try:
        with st.spinner("Thinking..."):
            result = answer(question, st.session_state.memory)

        rewritten = result.get("rewritten")
        if rewritten and rewritten != question:
            st.caption(f"Searching for: {rewritten}")

        st.markdown("### Answer")
        st.success(result["answer"])
        st.divider()

        with st.expander("Sources used"):
            for c in result.get("chunks", []):
                source_line = f"[{c.get('source')} p{c.get('page')}] {c.get('text', '')[:150]}"
                st.write(source_line)
    except Exception:
        st.error("Something went wrong. The model may be busy right now — please try again.")
