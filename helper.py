import os
import uuid

from llama_cloud_services import LlamaParse
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain.text_splitter import MarkdownHeaderTextSplitter

class FileStore:
    def __init__(self, path, llama_parse_key, openai_api_key):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.pdf_path = os.path.join(self.path, "pdf")
        if not os.path.exists(self.pdf_path):
            os.makedirs(self.pdf_path)

        self.md_path = os.path.join(self.path, "markdown")
        if not os.path.exists(self.md_path):
            os.makedirs(self.md_path)

        self.parser = LlamaParse(
            api_key=llama_parse_key,
            parse_mode="parse_page_with_agent",
            model="openai-gpt-5",
            high_res_ocr=True,
            adaptive_long_table=True,
            outlined_table_extraction=True,
            annotate_links=True,
            compact_markdown_table=True,
            extract_layout=False,
            language="vi"
        )

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai_api_key
        )
        connection = "postgresql+psycopg://langchain:langchain@localhost:5432/langchain"
        collection_name = "my_docs"
        self.vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
        )

        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
        self.text_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )

    def file_present(self):
        return len(os.listdir(self.md_path)) > 0

    def add_pdf(self, files):
        mds = []

        for file in files:
            filename = file.name
            safe_name = filename.replace(os.path.sep, "_")
            save_path = os.path.join(self.pdf_path, safe_name)

            if not os.path.exists(save_path):
                with open(save_path, "wb") as f:
                    f.write(file.read())

                md_results = self.parser.parse([os.path.join(self.pdf_path, i) for i in os.listdir(self.pdf_path)])
                langchain_doc = []

                for md in md_results:
                    md_docs = md.get_markdown_documents(split_by_page=True)

                    for count, doc in enumerate(md_docs):
                        path = os.path.join(self.md_path, safe_name.replace(".pdf", f"_{count}.md"))
                        mds.append(path)

                        with open(path, "w") as f:
                            f.write(doc.text)

                        langchain_doc.append(
                            Document(
                                page_content=doc.text,
                                metadata={"source": filename},
                                id=str(uuid.uuid4())
                            )
                        )

                self.vector_store.add_documents(langchain_doc)

    def get_json(self, prompt):
        return self.vector_store.similarity_search(prompt)