import os, tempfile
import pinecone
from pathlib import Path
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from dotenv import load_dotenv, dotenv_values
import streamlit as st
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()

TMP_DIR = Path(__file__).resolve().parent.joinpath('data', 'tmp')
LOCAL_VECTOR_STORE_DIR = Path(__file__).resolve().parent.joinpath('data', 'vector_store')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

st.set_page_config(page_title="RAG Engine", page_icon="🤖", layout="wide")
st.title("Retrieval Augmented Generation Engine")

def load_documents():
    loader = DirectoryLoader(TMP_DIR.as_posix(), glob='**/*.pdf')
    documents = loader.load()
    return documents

def split_documents(documents):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    return texts

def embeddings_on_local_vectordb(texts):
    vectordb = Chroma.from_documents(texts, embedding=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
                                     persist_directory=LOCAL_VECTOR_STORE_DIR.as_posix())
    retriever = vectordb.as_retriever(search_kwargs={'k': 7})
    return retriever

def embeddings_on_pinecone(texts):
    pinecone.init()
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Pinecone.from_documents(texts, embeddings, 'rag-pinecone')
    retriever = vectordb.as_retriever()
    return retriever

def query_llm(retriever, query):
    qa_chain = ConversationalRetrievalChain.from_llm(llm=OpenAI(openai_api_key=OPENAI_API_KEY), retriever=retriever, return_source_documents=True)
    result = qa_chain({'question': query, 'chat_history': st.session_state.chat_history})
    result = result['answer']
    st.session_state.messages.append((query, result))
    return result

def input_fields():
    #
    st.session_state.pinecone_db = st.toggle('Use Pinecone Vector DB')
    #
    st.session_state.source_docs = st.file_uploader(label="Upload Documents", type="pdf", accept_multiple_files=True)
    #

def process_documents():
    if not st.session_state.source_docs:
        st.warning("Please upload documents")
    else:
        try:
            TMP_DIR.mkdir(parents=True, exist_ok=True)
            
            for source_doc in st.session_state.source_docs:
                #
                with tempfile.NamedTemporaryFile(delete=False, dir=TMP_DIR.as_posix(), suffix='.pdf') as tmp:
                    tmp.write(source_doc.read())
                #
                documents = load_documents()
                #
                for _file in TMP_DIR.iterdir():
                    tmp_ = TMP_DIR.joinpath(_file)
                    tmp_.unlink()
                #
                texts = split_documents(documents)
                #
                if not st.session_state.pinecone_db:
                    st.session_state.retriever = embeddings_on_local_vectordb(texts)
                else:
                    st.session_state.retriever = embeddings_on_pinecone(texts)
        except Exception as e:
            st.error(f"Error: {e}")

def boot():
    #
    input_fields()
    #
    st.button("Submit Documents", on_click=process_documents)
    #
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    #
    if "messages" not in st.session_state:
        st.session_state.messages = []
    #
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    #
    for message in st.session_state.messages:
        st.chat_message('human').write(message[0])
        st.chat_message('ai').write(message[1])    
    #
    if query := st.chat_input():
        st.chat_message("human").write(query)
        response = query_llm(st.session_state.retriever, query)
        st.chat_message("ai").write(response)

if __name__ == '__main__':
    #
    boot()
