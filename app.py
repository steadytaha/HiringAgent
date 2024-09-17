import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection('gcs', type=FilesConnection)
df = conn.read("streamlit-bucket-10/Blog.csv", input_format="csv", ttl=600)

for row in df.itertuples():
    st.write(f"{row.Title} is in :{row.Category}: genre.")