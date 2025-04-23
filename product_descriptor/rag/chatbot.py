from product_descriptor.rag.chunk_handler import RecursiveCharacterTextSplitter
from product_descriptor.processing.static.prompts import chatbot_prompt
import concurrent.futures
from product_descriptor.config import config
from dotenv import load_dotenv
from numpy import dot
from numpy.linalg import norm
from openai import OpenAI
import concurrent
import numpy as np
import json
import streamlit as st
from sentence_transformers import SentenceTransformer
import os
load_dotenv()
client = OpenAI(api_key=st.secrets['openai'])
text_splitter = RecursiveCharacterTextSplitter()

# def create_embeddings(id:str):
#     path = os.path.join(config.XML_DATA_PATH,f"{id}.json")
#     with open(path,"r") as f:
#         data = json.load(f)
#     chunk = text_splitter.txt_loader(data["transcription"]["transcript"],id)
#     text_chunks = [i["text"] for i in chunk]
#     embeddings = client.embeddings.create(input = text_chunks,model = "text-embedding-ada-002")
#     for i,embedding in enumerate(embeddings.data):
#         chunk[i]["embedding"] = embedding.embedding
#     data["embeddings"] = chunk
#     with open(path,"w") as f:
#         json.dump(data,f)
#     return

embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


def create_embeddings(id: str):
    path = os.path.join(config.XML_DATA_PATH, f"{id}.json")

    # Load transcript data
    with open(path, "r") as f:
        data = json.load(f)

    # Split into chunks
    chunk = text_splitter.txt_loader(data["transcription"]["transcript"], id)
    text_chunks = [i["text"] for i in chunk]

    # Generate embeddings using HuggingFace model
    embeddings = embedding_model.encode(text_chunks)

    # Inject embeddings back into chunk structure
    for i, embedding in enumerate(embeddings):
        chunk[i]["embedding"] = embedding.tolist()  # JSON can't handle np arrays

    # Save the updated JSON
    data["embeddings"] = chunk
    with open(path, "w") as f:
        json.dump(data, f)

    return

def create_chatbot(ids:list):
    if(type(ids) == str):
        ids = [ids]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        result = list(executor.map(create_embeddings,ids))
    return result

# def retrieve_chunks(question:str,ids:list,top_k = 2):
#     all_chunks = []
#     question_embedding = client.embeddings.create(input = [question],model = "text-embedding-ada-002").data[0].embedding
#     for id in ids:
#         path = os.path.join(config.XML_DATA_PATH,f"{id}.json")
#         with open(path,"r") as f:
#             all_chunks.extend(json.load(f)["embeddings"])
    
#     similarity_scores = [cosine_similarity(question_embedding,i["embedding"]) for i in all_chunks]
#     return [x["text"] for _, x in sorted(zip(similarity_scores, all_chunks),reverse=True)][:top_k]
def cosine_similarity(a, b):
    a = np.array(a).flatten()
    b = np.array(b).flatten()
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_chunks(question: str, ids: list, top_k: int = 2):
    all_chunks = []

    # Encode the query locally
    question_embedding = embedding_model.encode([question])[0]

    # Load all chunks from given IDs
    for id in ids:
        path = os.path.join(config.XML_DATA_PATH, f"{id}.json")
        with open(path, "r") as f:
            all_chunks.extend(json.load(f)["embeddings"])

    # Compute similarity scores
    similarity_scores = [
        cosine_similarity([question_embedding], [chunk["embedding"]])
        for chunk in all_chunks
    ]

    # Sort and return top-k most relevant texts
    top_chunks = [x["text"] for _, x in sorted(zip(similarity_scores, all_chunks), reverse=True)][:top_k]
    return top_chunks

def ask_question(question:str, ids:list):
    chunks = retrieve_chunks(question,ids)
    context = "\n\n".join(chunks)
    response = client.chat.completions.create(
        messages = [
            {"role" : "system","content":chatbot_prompt.format(chunk=context)},
            {"role": "user", "content": question},
        ],
        model="gpt-4o-mini-2024-07-18"
    )    
    return response.choices[0].message.content
    
    
        
    