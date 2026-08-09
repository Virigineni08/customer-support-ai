import os
import sys
from dotenv import load_dotenv
from groq import Groq

sys.path.append(os.path.dirname(__file__))
from agents import AGENTS

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_intent(query):
    """Asks the LLM to classify which agent(s) should handle this query."""
    agent_list = ", ".join(AGENTS.keys())

    prompt = f"""Classify the customer query below into one or more of these categories: {agent_list}.
Respond with ONLY the matching category names, comma-separated, nothing else.

Query: "{query}"

Categories:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip().lower()
    detected = [cat.strip() for cat in raw.split(",") if cat.strip() in AGENTS]

    return detected if detected else ["faq"]  # fallback to FAQ if nothing matches

if __name__ == "__main__":
    test_queries = [
        "I paid yesterday but Premium is still locked.",
        "My password reset email never arrived.",
        "What's your refund policy?",
        "This product is terrible and I want to complain!",
    ]

    for q in test_queries:
        agents = detect_intent(q)
        print(f"Query: {q}")
        print(f"Routed to: {agents}\n")