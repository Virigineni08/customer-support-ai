import os
import sys
import pickle
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

sys.path.append(os.path.dirname(__file__))
from agents import AGENTS
from router import detect_intent

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load the RAG index (built earlier in backend/rag/)
RAG_DIR = os.path.join(os.path.dirname(__file__), "..", "rag")
index = faiss.read_index(os.path.join(RAG_DIR, "faiss_index.bin"))
with open(os.path.join(RAG_DIR, "chunks.pkl"), "rb") as f:
    chunks = pickle.load(f)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query, top_k=3):
    query_vector = embed_model.encode([query])
    distances, indices = index.search(query_vector, top_k)
    return [chunks[idx] for idx in indices[0]]

def answer_query(query):
    # Step 1: figure out which agent(s) handle this
    intents = detect_intent(query)
    primary_agent = AGENTS[intents[0]]  # use the first matched agent as the lead voice

    # Step 2: retrieve relevant context from the knowledge base
    context_chunks = retrieve(query)
    context = "\n\n".join(context_chunks)

    # Step 3: build the agent-specific prompt
    prompt = f"""{primary_agent['system_prompt']}

Use the following context to answer the customer's question. If the context doesn't contain the answer, say you don't have that information and offer to escalate.

Context:
{context}

Customer question: {query}

Answer:"""

    # Step 4: generate the final answer
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return {
        "query": query,
        "routed_to": intents,
        "agent_used": primary_agent["name"],
        "answer": response.choices[0].message.content
    }

if __name__ == "__main__":
    test_queries = [
        "I paid yesterday but Premium is still locked.",
        "What's your refund policy?",
        "This product is terrible, I want a refund now!",
    ]

    for q in test_queries:
        result = answer_query(q)
        print(f"Query: {result['query']}")
        print(f"Routed to: {result['routed_to']}")
        print(f"Agent used: {result['agent_used']}")
        print(f"Answer: {result['answer']}\n")
        print("-" * 60)