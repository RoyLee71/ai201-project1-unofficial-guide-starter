# ingest.py
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCUMENTS_DIR = "documents"


def load_documents(folder=DOCUMENTS_DIR):
    """Load all .txt files from the documents folder."""
    docs = []
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
        docs.append({"text": raw_text, "source": filename})
        print(f"  Loaded: {filename} ({len(raw_text)} chars)")
    return docs


def clean_text(text):
    """Remove boilerplate, navigation, and noise from raw document text."""
    # Decode common HTML entities
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    text = text.encode("utf-8", errors="replace").decode("utf-8")
    text = text.replace("\u2019", "'").replace("\u2018", "'")  # smart quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')  # smart double quotes
    text = text.replace("\u2013", "-").replace("\u2014", "-")  # em/en dashes
    text = text.replace("\xe2\x80\x99", "'")                  # utf-8 artifact

    # Remove any residual HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove common navigation/boilerplate patterns
    boilerplate_patterns = [
        r"Skip to (main )?content",
        r"Skip to navigation",
        r"Sign (in|up)",
        r"Subscribe (now|today)",
        r"Cookie (Policy|Settings)",
        r"Share (this|on)",
        r"Follow us on",
        r"Copyright ©.*",
        r"All rights reserved",
        r"Read more",
        r"Click here",
        r"Advertisement",
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+\w+ \d+,\s+\d{4}",  # datelines
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Collapse 3+ blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace on each line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    # Remove very short lines that are likely nav items (under 4 characters)
    lines = [line for line in text.splitlines() if len(line) > 3 or line == ""]
    text = "\n".join(lines)

    return text.strip()


def chunk_documents(docs, chunk_size=400, overlap=100):
    """
    Split cleaned documents into chunks using paragraph-first strategy,
    falling back to fixed-size character splitting.
    Attaches source filename metadata to every chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # paragraph → sentence → word → char
    )

    chunks = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        split_texts = splitter.split_text(cleaned)
        for chunk_text in split_texts:
            chunk_text = chunk_text.strip()
            if len(chunk_text) > 20:   # skip near-empty fragments
                chunks.append({
                    "text": chunk_text,
                    "source": doc["source"]
                })

    return chunks


if __name__ == "__main__":
    print("=== Loading documents ===")
    docs = load_documents()
    print(f"\nLoaded {len(docs)} documents\n")

    print("=== Chunking ===")
    chunks = chunk_documents(docs)
    print(f"Total chunks: {len(chunks)}\n")

    print("=== Validation: 5 random chunks ===")
    import random
    sample = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"--- Chunk {i} (source: {chunk['source']}) ---")
        print(chunk["text"])
        print()