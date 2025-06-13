from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env (especially Google api key)

# Create Google Gemini LLM model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.environ['GOOGLE_API_KEY'], temperature=0.1)

# # Initialize instructor embeddings using the Hugging Face model
instructor_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectordb_file_path = "faiss"

def create_vector_db():
    # Load data from FAQ sheet
    loader = CSVLoader(file_path='Psychology.csv', source_column="Context", encoding='cp437')
    try:
        data = loader.load()
    except RuntimeError as e:
        print(f"Failed to load CSV: {e}")
        return

    # Create a FAISS instance for vector database from 'data'
    vectordb = FAISS.from_documents(data, instructor_embeddings)

    # Save vector database locally
    vectordb.save_local(vectordb_file_path)

def get_qa_chain():
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(vectordb_file_path, instructor_embeddings, allow_dangerous_deserialization=True)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.8)  

    statement_template = ("""You are an expert mental health chatbot that provides empathetic, professional, and supportive responses to users seeking help with emotional well-being.

    Your main goals:

    Respond kindly, without making assumptions about the user's emotions unless clearly expressed.

    Keep responses short, clear, and conversational.

    Provide helpful suggestions and ask open-ended questions to better understand the user’s needs.

    Use bullet points to share lists or techniques.

    Offer affirmations, strategies, or insights only when the user shows interest or when it's clearly appropriate.

    Always validate the user’s input and maintain a friendly, safe tone.

    If the user says "hi", respond with a warm greeting — do not assume emotional state. If the user asks about a topic (e.g., affirmations), provide concise and engaging info and ask if they’d like to explore more. Avoid suggesting causes like anxiety, stress, depression unless the user directly mentions them.

    Context: {context}
    
    Question: {question}""")

    prompt = PromptTemplate(
        template=statement_template, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        input_key="query",
        retriever=retriever,
        verbose=True,
        chain_type_kwargs={"prompt": prompt},
    )
    
    return qa_chain

if __name__ == "__main__":
    # create_vector_db()
    chain = get_qa_chain()
    print(chain)