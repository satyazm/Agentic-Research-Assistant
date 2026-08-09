import os

import streamlit as st

from agentic_crew import run
from chart_runner import extract_and_run_chart

st.set_page_config(page_title="AI Research Assistant", page_icon="🧬", layout="wide")

# Local directory where uploaded / downloaded papers live.
os.makedirs("papers", exist_ok=True)

st.title("🧬 Agentic Academic Research Assistant")
st.markdown("Navigate arXiv or analyze local papers with an expert multi-agent team.")

with st.sidebar:
    st.header("Research Assets")
    uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])

    if uploaded_file:
        file_path = os.path.join("papers", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' ready for analysis.")

    st.divider()
    st.info(
        "An LLM planner turns your request into a task plan, then a crew of "
        "specialist agents executes it step by step."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay conversation history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("chart"):
            st.image(message["chart"])

if prompt := st.chat_input("What would you like to research?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Planning and executing research workflow...", expanded=True) as status:
            try:
                result = run(
                    user_input=prompt,
                    file_name=uploaded_file.name if uploaded_file else None,
                )
                result_str = str(result)
                status.update(label="Research Complete!", state="complete", expanded=False)

                st.markdown(result_str)

                # If the visualization agent emitted matplotlib code, run it.
                chart_path = extract_and_run_chart(result_str)
                if chart_path:
                    st.image(chart_path, caption="Generated Comparison Chart")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result_str,
                    "chart": chart_path,  # None when there is no chart
                })

            except Exception as e:
                st.error(f"An error occurred: {e}")
                status.update(label="Research Failed", state="error")

if st.session_state.messages and st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
