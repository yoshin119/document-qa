import os

from langchain_community.document_loaders import PyPDFLoader

class FileStore:
    def __init__(self, path):
        self.path = path

    def file_present(self):
        return len(os.listdir(self.path)) > 0

    def get_file(self):
        first_filename = os.listdir(self.path)[0]
        first_filepath = os.path.join(self.path, first_filename)

        loader = PyPDFLoader(first_filepath)

        return loader.load()[0]