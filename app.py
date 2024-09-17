import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection('gcs', type=FilesConnection)
documents = conn.read("streamlit-bucket-10/Test/", input_format="pdf", ttl=600)

st.write(documents)

"""for row in df.itertuples():
    st.write(f"{row.Title} is in {row.Category} genre.")"""