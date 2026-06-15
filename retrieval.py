# retrieval.py
import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

# ── Constants ────────────────────────────────────────────────────────────────
CHROMA_DIR      = "./chroma_db"
COLLECTION_NAME = "offcampus_housing"
EMBED_MODEL     = "all-MiniLM-L6-v2"

# ── Load model once at module level (reused across calls) ─────────────────────
print("Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)
print("Model ready.")


def build_index(chunks):
    """
    Embed all chunks and store them in ChromaDB with source metadata.
    Safe to re-run — clears and rebuilds the collection each time.
    """
    client     = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection so we can rebuild cleanly
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Cleared existing collection.")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}   # cosine similarity
    )

    texts     = [c["text"]   for c in chunks]
    sources   = [c["source"] for c in chunks]
    ids       = [f"chunk_{i}" for i in range(len(chunks))]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # Add in batches of 100 to avoid memory issues
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        collection.add(
            ids        = ids[i:i+batch_size],
            embeddings = embeddings[i:i+batch_size],
            documents  = texts[i:i+batch_size],
            metadatas  = [{"source": s} for s in sources[i:i+batch_size]]
        )

    print(f"Index built — {collection.count()} chunks stored in ChromaDB.")
    return collection


def get_collection():
    """Load the existing ChromaDB collection (must call build_index first)."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)


def retrieve(query, k=5):
    """
    Embed a query and return the top-k most relevant chunks.
    Returns a list of dicts: {text, source, distance}
    Lower distance = more relevant (cosine distance, 0–2 scale).
    """
    collection     = get_collection()
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = k,
        include          = ["documents", "metadatas", "distances"]
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text":     text,
            "source":   meta["source"],
            "distance": round(dist, 4)
        })

    return chunks


# ── Main: build index then test retrieval ─────────────────────────────────────
if __name__ == "__main__":

    # 1. Build the index from your documents
    print("\n=== Building index ===")
    docs   = load_documents()
    chunks = chunk_documents(docs)
    build_index(chunks)

    # 2. Test retrieval with your 3 evaluation questions
    TEST_QUERIES = [
        "What do students say about landlord response time for maintenance?",
        "What are the most common reasons students lose their security deposit?",
        "What hidden costs beyond rent do students get surprised by?",
    ]

    print("\n=== Retrieval Test ===\n")
    for query in TEST_QUERIES:
        print(f"QUERY: {query}")
        print("-" * 60)
        results = retrieve(query, k=5)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] distance={r['distance']} | source={r['source']}")
            print(f"      {r['text'][:200]}...")
            print()
        print()