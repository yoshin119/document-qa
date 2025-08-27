import streamlit as st
import json
import os

from openai import OpenAI
from helper import FileStore

tab_main, tab_file = st.tabs(["Main", "File Upload"])

fileStore = FileStore("FileStore")

with tab_main:
    st.title("📄 Document question answering")

    openai_api_key = st.secrets["openai_api_key"]
    client = OpenAI(api_key=openai_api_key)

    if (prompt := st.chat_input("Câu hỏi về file:")) and fileStore.file_present():
        uploaded_file = fileStore.get_file()
        document = {}

        init_prompt = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }, {
                "role": "developer",
                "content": f"Extract information from the following json and answer questions: {document}"
            }
        ]

        with st.chat_message("user"):
            st.markdown(prompt)

        st.write("Current File:", uploaded_file.metadata["source"].split("/")[-1])

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="gpt-5-nano",
                messages=init_prompt,
                stream=True
            )

            response = st.write_stream(stream)

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