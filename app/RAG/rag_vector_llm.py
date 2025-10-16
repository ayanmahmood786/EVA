from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"RAG/.env")
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import shutil
 
from langchain_core.runnables import RunnablePassthrough
import re
import time
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings


# os.remove(r"D:\New Folder\RAG\chroma")
file_path=r"D:\RAG\PDF\inventory\Inventory v7.4.pdf"
PATH="chroma"
os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"]=os.getenv('LANGCHAIN_TRACING_V2')
os.environ["LANGCHAIN_ENDPOINT"]=os.getenv('LANGCHAIN_ENDPOINT')
os.environ["LANGCHAIN_API_KEY"]=os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"]=os.getenv('LANGCHAIN_PROJECT')
tokens=""
# os.environ['HF_TOKEN'] = ''
from huggingface_hub import login

login(os.getenv("HF_TOKEN"))
# embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
def pdf_loader(file_path):
    # loader = PyPDFLoader(file_path)
    loader = PyMuPDFLoader(file_path)
    # loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages


def spiltter(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=120, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    return all_splits

def vector_stored(all_splits,embeddings,PATH):
    try:
        if os.path.isfile(PATH):
            os.remove(PATH)
        if os.path.exists(PATH):
            shutil.rmtree(PATH)

        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings,persist_directory=PATH,collection_name="My_collection")
        return vectorstore
# except PermissionError as e:
    #     if "[WinError 32]" in str(e):
    #         vectorstore=Chroma(persist_directory=PATH,embedding_function=embeddings,collection_name="My_collection")
#         vectorstore.delete_collection()
    #         vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings,persist_directory=PATH,collection_name="My_collection")
            # return vectorstore
    except Exception as e:
        vectorstore=Chroma(persist_directory=PATH,embedding_function=embeddings,collection_name="My_collection")
        vectorstore.delete_collection()
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings,persist_directory=PATH,collection_name="My_collection")
        return vectorstore




def model(vt,question):
    # retriever = vt.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    # system_prompt = (
    #     "You are an assistant for question-answering tasks. "
    #     "Use the following pieces of retrieved context to answer "
    #     "the question. If you don't know the answer, say that you "
    #     "don't know. Use three sentences maximum and keep the "
    #     "answer concise."
    #     ""
    #     "\n\n"
    #     "{context}"
    # )

    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", system_prompt),
    #         ("human", "{input}"),
    #     ]
    # )
    # # print(results[0][1])

    # question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    # response = rag_chain.invoke({"input":question})
    # return response
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    retriever = vt.as_retriever()
    system_prompt = (
        """User Question:{question}
        Provide a Detailed and Precise Answer in around 100-200 words and in points if possible. 
        Use the following pieces of retrieved context to answer. 
        the question. If you don't know the answer, say that you 
        don't know.If you dont know Just say the area is out of context and please try again in 30-50 words.
        No need to provide any additional or important notes.
        \n\n
        
        CONTEXT:
        {context}"""
    )
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain=(
    {"context": retriever | format_docs, "question":RunnablePassthrough()} | prompt | llm )
    response=chain.invoke(question)
    return response
