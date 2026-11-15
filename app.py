import os
from datetime import datetime

import requests
import streamlit as st

BASE_URL = os.getenv("TRAVEL_API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("TRAVEL_API_TIMEOUT", "90"))

st.set_page_config(
    page_title="Travel Planner",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🌍 AI Travel Planner")
st.caption("Create a practical itinerary using live travel information.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Connection")
    st.code(BASE_URL)
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("e.g. Plan a five-day trip to Goa")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Researching your trip..."):
            try:
                response = requests.post(
                    f"{BASE_URL}/query",
                    json={"question": user_input},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                answer = response.json().get("answer")
                if not answer:
                    raise ValueError("The API returned an empty answer.")
            except requests.RequestException as exc:
                answer = (
                    "I could not reach the travel API. "
                    f"Check that the backend is running at `{BASE_URL}`. "
                    f"Details: {exc}"
                )
                st.error(answer)
            except (ValueError, KeyError) as exc:
                answer = f"The travel API returned an invalid response: {exc}"
                st.error(answer)
            else:
                st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
