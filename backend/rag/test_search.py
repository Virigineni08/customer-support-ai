from sentence_transformers import SentenceTransformer
import faiss
import pickle

# Load the saved index and chunks
index = faiss.read_index("faiss_index.bin")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=3):
    query_vector = model.encode([query])
    distances, indices = index.search(query_vector, top_k)
    print(f"\nQuery: {query}\n")
    for rank, idx in enumerate(indices[0]):
        print(f"--- Result {rank+1} (distance: {distances[0][rank]:.2f}) ---")
        print(chunks[idx])
        print()

if __name__ == "__main__":
    search("How big is a Walgreens store?")