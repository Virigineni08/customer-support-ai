import os
from sentence_transformers import SentenceTransformer
import faiss
import pickle

KB_DIR = "../../knowledge_base"
CHUNK_SIZE = 500  # characters per chunk

def load_documents():
    texts = []
    for filename in os.listdir(KB_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(KB_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                texts.append((filename, content))
    return texts

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def main():
    print("Loading documents...")
    documents = load_documents()

    all_chunks = []
    for filename, content in documents:
        chunks = chunk_text(content)
        for c in chunks:
            if c.strip():
                all_chunks.append(c)

    print(f"Total chunks created: {len(all_chunks)}")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, "faiss_index.bin")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)

    print("Done! Index saved as faiss_index.bin, chunks saved as chunks.pkl")

if __name__ == "__main__":
    main()