import os
from io import StringIO
import streamlit as st
from google.cloud import storage
from dotenv import load_dotenv, dotenv_values
from st_files_connection import FilesConnection

def upload_blob(bucket_name, destination_blob_name, file):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_file(file)

    print(f"File {destination_blob_name} uploaded to {bucket_name}.")
    st.write("File:  ", destination_blob_name, "  uploaded.")

st.title('Upload Files to Google Cloud Storage using Streamlit')

# load variables from .env file
load_dotenv()

bucket_name = os.environ["BUCKET_NAME"]
print(bucket_name)

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    print(uploaded_file.name)
    upload_blob(bucket_name, uploaded_file.name, uploaded_file)


def list_files(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    files = [blob.name for blob in bucket.list_blobs()]
    return files

# Display the list of files in the bucket
st.write("Files in your Google Cloud Storage bucket:")
files = list_files(bucket_name)
selected_file = st.selectbox("Select a file to download", files)

# Download the selected file upon clicking the download button
if st.button("Download File"):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(selected_file)
    blob.download_to_filename(selected_file)
    st.success(f"File '{selected_file}' downloaded successfully.")
