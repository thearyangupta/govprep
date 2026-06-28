import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="GovPrep AI", page_icon="study", layout="wide")

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

with st.sidebar:
    st.title("GovPrep AI")
    st.write("AI study assistant for UPSC/CDS prep.")
    st.write("Sources: NCERT Polity, History, Geography")
    st.divider()
    if st.button("Reset conversation"):
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
            response = requests.post(
                API_URL,
                json={"question": question}
            )
            result = response.json()

        rewritten = result.get("rewritten")
        if rewritten and rewritten != question:
            st.caption(f"Searching for: {rewritten}")

        st.markdown("### Answer")
        st.success(result["answer"])
        st.divider()

        with st.expander("Sources used"):
            for s in result.get("sources", []):
                source_line = f"[{s.get('source')} p{s.get('page')}]"
                st.write(source_line)

    except Exception:
        st.error("Something went wrong. The model may be busy right now — please try again.")