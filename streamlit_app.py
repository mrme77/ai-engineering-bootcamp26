"""Neon green Streamlit interface for the bootcamp study assistant."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from ask_client import request_answer


def main() -> None:
    """Render the question form and display the backend's answer and usage."""
    load_dotenv(Path(__file__).with_name(".env"))
    api_url = os.environ.get("ASK_API_URL", "http://127.0.0.1:8000")
    st.set_page_config(page_title="Bootcamp study lab", page_icon="🌱", layout="wide")
    # Keep the neon button readable using the project's configured dark color.
    st.html(
        "<style>:root {--lab-ink: "
        + str(st.get_option("theme.backgroundColor"))
        + ";} button[kind='primaryFormSubmit'] {color: var(--lab-ink); font-weight: 700;}</style>"
    )
    st.title("Bootcamp study lab")
    st.write("Bring a question. Build your understanding.")
    st.caption("Ask about a bootcamp concept, explore an example, or work through a problem.")

    with st.form("ask_form"):
        question = st.text_area(
            "What are you working on?",
            placeholder="For example: How does retrieval help an LLM answer questions about my notes?",
            height=150,
        )
        submitted = st.form_submit_button("Ask the study lab", type="primary")

    if submitted:
        if not question.strip():
            st.warning("Enter a question before asking the study lab.")
        else:
            try:
                with st.spinner("Working through your question..."):
                    result = request_answer(api_url, question.strip())
            except ValueError as exc:
                st.error(str(exc))
            else:
                with st.container(border=True):
                    st.subheader("Your answer")
                    st.markdown(result.answer)
                tokens, cost = st.columns(2)
                tokens.metric("Tokens used", f"{result.tokens_used:,}")
                cost.metric("Call cost (USD)", f"${result.cost_usd:.8f}")
                st.caption(f"Model: {result.model}. Usage and cost reported by OpenRouter.")

    st.divider()
    st.caption("Each submitted question makes one model request. Reading and editing your question makes no model calls.")


if __name__ == "__main__":
    main()
