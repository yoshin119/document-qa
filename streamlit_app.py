import streamlit as st
import json
import os

from openai import OpenAI

tab_main, tab_file = st.tabs(["Main", "File Upload"])

with tab_main:
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

UPLOAD_FOLDER = "FileStore"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

with tab_file:
    st.title("Upload files (pdf)")

    uploaded_files = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        accept_multiple_files=True
    )

    for uploaded_file in uploaded_files:
        save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())