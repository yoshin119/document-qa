import streamlit as st
import os

from openai import OpenAI
from helper import FileStore

st.set_page_config(layout="wide")

tab_main, tab_file = st.tabs(["Main", "File Upload"])

llama_parse_key = st.secrets["llama_parse_key"]
openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

UPLOAD_FOLDER = "FileStore"
fileStore = FileStore(
    UPLOAD_FOLDER,
    llama_parse_key,
    openai_api_key
)

with tab_main:
    st.title("📄 Document question answering")

    document = None

    if fileStore.file_present():
        col1, col2 = st.columns(
            [0.6, 0.4],
            gap="medium",
            border=True
        )

        with col1:
            if (prompt := st.chat_input("Câu hỏi về file:")):
                uploaded_file = fileStore.get_json(prompt)

                document = "/n/n".join([file.page_content for file in uploaded_file])

                with st.chat_message("user"):
                    st.markdown(prompt)

                st.write("Current File:", ", ".join(list(set([file.metadata["source"] for file in uploaded_file]))))

                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model="gpt-5-nano",
                        messages=[
                            {
                                "role": "developer",
                                "content": f"Extract information from the following markdown and answer questions: {document}"
                            }, {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        stream=True
                    )

                    response = st.write_stream(stream)

        with col2:
            st.subheader("References:")
            if document is None:
                st.write("...")
            else:
                st.write(document)
    else:
        st.write("Chưa có file, up bên tab File Upload")

with tab_file:
    st.title("Upload files (pdf)")

    uploaded_files = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Processing...", show_time=True):
            fileStore.add_pdf(uploaded_files)

        st.markdown('Upload complete!')
        st.markdown(
            '''
                <style>
                    .stFileUploaderFile {display: none}
                <style>
            ''',
            unsafe_allow_html=True
        )

        uploaded_files = False

    st.divider()

    items = os.listdir(fileStore.pdf_path)

    with st.container(border=True):
        st.subheader("Uploaded", anchor=False)

        for item in items:
            st.markdown("- " + item)