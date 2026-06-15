# query.py
import os
from groq import Groq
from dotenv import load_dotenv
from retrieval import retrieve

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an assistant that helps college students understand 
off-campus housing experiences based exclusively on real student accounts.

STRICT RULES:
- Answer ONLY using the information in the provided documents below.
- Do NOT use any outside knowledge, general advice, or your training data.
- If the documents do not contain enough information to answer the question, 
  respond with exactly: "I don't have enough information on that in my documents."
  Do NOT append a Sources line when declining.
- Always cite which document(s) your answer draws from at the end of your response,
  using the format: Sources: [filename1, filename2]
- List each source filename only ONCE, even if you drew from it multiple times.
- Be specific and quote or closely paraphrase the student experiences in the documents.
- Do not make up details, statistics, or experiences not present in the documents."""

def build_context(chunks):
    """Format retrieved chunks into a numbered context block for the prompt."""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"[Document {i} — {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(lines)


def ask(question, k=5):
    """
    Retrieve relevant chunks, then generate a grounded answer using Groq.
    Returns {"answer": str, "sources": list[str], "chunks": list[dict]}
    """
    # 1. Retrieve top-k relevant chunks
    chunks = retrieve(question, k=k)

    # 2. Build the context string from retrieved chunks
    context = build_context(chunks)

    # 3. Build the user message with context + question
    user_message = f"""Here are the relevant documents:

{context}

Question: {question}

Remember: answer only from the documents above. Cite your sources at the end."""

    # 4. Call Groq
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,   # low temperature = more faithful to source material
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    # 5. Collect unique source filenames from retrieved chunks
    sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks,   # kept for debugging
    }


# ── Grounding tests ───────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Test 1: question your documents CAN answer
    print("=" * 60)
    print("TEST 1 — In-scope query")
    print("=" * 60)
    result = ask("What do students say about landlord response time for maintenance?")
    print("ANSWER:\n", result["answer"])
    print("\nSOURCES:", result["sources"])

    # Test 2: another in-scope query
    print("\n" + "=" * 60)
    print("TEST 2 — In-scope query")
    print("=" * 60)
    result = ask("What are the most common reasons students lose their security deposit?")
    print("ANSWER:\n", result["answer"])
    print("\nSOURCES:", result["sources"])

    # Test 3: question your documents CANNOT answer (grounding check)
    print("\n" + "=" * 60)
    print("TEST 3 — Out-of-scope query (should decline)")
    print("=" * 60)
    result = ask("What is the average rent for a studio apartment in New York City?")
    print("ANSWER:\n", result["answer"])
    print("\nSOURCES:", result["sources"])