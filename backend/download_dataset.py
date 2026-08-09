from datasets import load_dataset
import os

# Load a small slice of MS MARCO (v1.1, validation split, first 300 examples)
print("Downloading MS MARCO sample...")
dataset = load_dataset("microsoft/ms_marco", "v1.1", split="validation[:300]")
os.makedirs("../knowledge_base", exist_ok=True)

count = 0
with open("../knowledge_base/msmarco_passages.txt", "w", encoding="utf-8") as f:
    for row in dataset:
        query = row["query"]
        passages = row["passages"]["passage_text"]
        for p in passages:
            f.write(f"Q: {query}\n")
            f.write(f"Passage: {p}\n\n")
            count += 1

print(f"Saved {count} passages to knowledge_base/msmarco_passages.txt")