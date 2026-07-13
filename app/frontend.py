import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="GovPrep AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top right, #172554 0%, #020617 45%, #020617 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #1e293b;
}

.main-title {
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 28px;
    font-weight: 700;
    color: #e5e7eb;
}

.small-text {
    color: #cbd5e1;
    font-size: 18px;
}

.example-card {
    padding: 22px;
    border: 1px solid #334155;
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.75);
    min-height: 90px;
    font-size: 18px;
}

.answer-box {
    padding: 24px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(34,197,94,0.25), rgba(20,83,45,0.55));
    border-left: 5px solid #22c55e;
    font-size: 18px;
    line-height: 1.7;
}

.source-row {
    padding: 14px 18px;
    border: 1px solid #1e293b;
    border-radius: 12px;
    background: rgba(15,23,42,0.8);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

with st.sidebar:
    st.markdown("## 🎓 GovPrep AI")
    st.write("AI study assistant for UPSC/CDS prep.")
    st.write("Sources: NCERT Polity, History, Geography")
    st.divider()

    st.markdown("### 📚 Sources")
    st.write("📘 NCERT Polity")
    st.write("📙 NCERT History")
    st.write("📗 NCERT Geography")

    st.divider()

    if st.button("🔄 Reset conversation"):
        st.session_state.question_input = ""
        st.rerun()

    st.markdown("---")
    st.info("Stay consistent, stay ahead.")

st.markdown('<div class="main-title">GovPrep AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">NCERT Doubt Solver</div>', unsafe_allow_html=True)
st.markdown('<p class="small-text">Ask about NCERT Polity, History, and Geography.</p>', unsafe_allow_html=True)

st.markdown("### ✨ Try asking:")

examples = [
    "What are fundamental rights?",
    "Ancient Indian History?",
    "Atmospheric layers?",
]

col1, col2, col3 = st.columns(3)

for col, example in zip((col1, col2, col3), examples):
    with col:
        if st.button(example, use_container_width=True):
            st.session_state.question_input = example

st.markdown("### Your question:")

question = st.text_input(
    label="Your question:",
    key="question_input",
    label_visibility="collapsed"
)

if st.button("🚀 Ask", use_container_width=False):
    question = st.session_state.question_input

if question:
    try:
        with st.spinner("Thinking..."):
            response = requests.post(
                API_URL,
                json={"question": question}
            )
            result = response.json()

        if "answer" not in result:
            st.error(result.get("detail", "API did not return an answer"))

        else:
            rewritten = result.get("rewritten")
            if rewritten and rewritten != question:
                st.caption(f"Searching for: {rewritten}")

            st.markdown("## ✅ Answer")
            st.markdown(
                f'<div class="answer-box">{result["answer"]}</div>',
                unsafe_allow_html=True
            )

            st.divider()

            st.markdown("## 📚 Sources used")

            sources = result.get("sources", [])

            if sources:
                for s in sources:
                    source = s.get("source", "unknown source")
                    page = s.get("page", "?")
                    text = s.get("text", "")

                    st.markdown(
                        f"""
                        <div class="source-row">
                            <b>📄 {source}</b> &nbsp; | &nbsp;
                            Page {page}<br>
                            <span style="color:#cbd5e1;">{text[:220]}...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No sources returned by API.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")