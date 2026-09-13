import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/support"


st.set_page_config(
    page_title="AI Customer Support",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Customer Support")
st.caption("Model-routed customer support assistant")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant" and "runtime" in message:
            runtime = message["runtime"]

            st.caption(
                f"Model: {runtime['model']}  |  "
                f"Latency: {runtime['latency_ms']} ms  |  "
                f"Retries: {runtime['retries']}  |  "
                f"Fallback: {runtime['fallback']}"
            )


prompt = st.chat_input(
    "Ask about an order, payment, cancellation, or refund..."
)


if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = requests.post(
            API_URL,
            json={"message": prompt},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        with st.chat_message("assistant"):
            st.write(data["answer"])

            runtime = data["runtime"]

            st.caption(
                f"Model: {runtime['model']}  |  "
                f"Latency: {runtime['latency_ms']} ms  |  "
                f"Retries: {runtime['retries']}  |  "
                f"Fallback: {runtime['fallback']}"
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": data["answer"],
            "runtime": runtime,
        })

    except Exception as error:

        with st.chat_message("assistant"):
            st.error(f"API error: {error}")