import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from groq import Groq

# Load your API key from .env
load_dotenv(dotenv_path="../.env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load the FAISS index and chunks
index = faiss.read_index("faiss_index.bin")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query, top_k=3):
    query_vector = embed_model.encode([query])
    distances, indices = index.search(query_vector, top_k)
    return [chunks[idx] for idx in indices[0]]

def generate_answer(query):
    retrieved_chunks = retrieve(query)
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""Use the following context to answer the question. If the context doesn't contain the answer, say you don't have that information.

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    question = "How big is a Walgreens store?"
    answer = generate_answer(question)
    print(f"\nQuestion: {question}\n")
    print(f"Answer: {answer}\n")