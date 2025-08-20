import streamlit as st
import base64
import json

from openai import OpenAI

st.title("📄 Document question answering")

openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-5-nano"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt_dict := st.chat_input("Câu hỏi về file:", accept_file=True, file_type="json"):
    prompt = prompt_dict["text"]
    init_prompt = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }

    if len(uploaded_file_list := prompt_dict["files"]) == 1:
        uploaded_file = uploaded_file_list[0]
        document = json.dumps(json.load(uploaded_file))

        st.session_state.messages.append(
            {
                "role": "developer",
                "content": f"Extract information from the following json and answer questions: {document}"
            }
        )

    st.session_state.messages.append(init_prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})