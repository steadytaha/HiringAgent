import os
from io import StringIO
import streamlit as st
from google.cloud import storage
from dotenv import load_dotenv, dotenv_values
from st_files_connection import FilesConnection

conn = st.connection('gcs', type=FilesConnection)
"""for row in df.itertuples():
    st.write(f"{row.Title} is in {row.Category} genre.")"""

def upload_blob(bucket_name, destination_blob_name, file):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_file(file)

    print(f"File {destination_blob_name} uploaded to {bucket_name}.")
    st.write("File:  ", destination_blob_name, "  uploaded.")


"""WEB UI"""


st.title('Upload Files to Google Cloud Storage using Streamlit')

# load variables from .env file
load_dotenv()

bucket_name = os.environ["BUCKET_NAME"]
print(bucket_name)

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    print(uploaded_file.name)
    upload_blob(bucket_name, uploaded_file.name, uploaded_file)