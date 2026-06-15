# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Off-campus housing is one of the most consequential decisions a college student makes, yet the information they need most like: how landlords actually respond to maintenance requests, which lease clauses cause problems, what hidden costs to expect; lives almost entirely in student conversations, newspaper threads, and Reddit posts rather than in anything a university publishes. Official housing pages list available properties but don't tell which landlords ignore mold complaints for six months or that your deposit disappears if you miss a cleaning clause buried on page 4 of the lease. This system makes that hard-won peer knowledge searchable and answerable.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                                                           | Description                                                              | URL or location                                                                             |
| --- | ---------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 1   | Reddit r/college — off-campus housing (top posts)                | Student posts and comments about real apartment experiences              | https://www.reddit.com/r/college/search/?q=off+campus+housing&restrict_sr=1&sort=top        |
| 2   | "They do the bare minimum" — Penn students vs. landlords (DP)    | Student quotes about maintenance failures at Campus Apartments           | https://www.thedp.com/article/2024/03/penn-off-campus-housing-landlord-issues               |
| 3   | Students share their housing horror stories (BYU Daily Universe) | Student anecdotes: fines, threats of eviction, ignored maintenance       | https://universe.byu.edu/2017/08/22/students-share-their-housing-horror-stories/            |
| 4   | When housing gets weird: 5 strange off-campus stories (DP)       | Short student anecdotes about unexpected off-campus situations           | https://www.thedp.com/article/2015/10/when-housing-gets-weird                               |
| 5   | MIT ChemE Off-Campus Housing Student Guide (PDF)                 | Peer-written guide with advice from current MIT students                 | https://cheme.mit.edu/wp-content/uploads/2021/03/Off-campus-housing.pdf                     |
| 6   | How to work with an off-campus landlord (DP)                     | Student experiences and advice on communicating with landlords           | https://www.thedp.com/article/2005/02/how_to_work_with_an_offcampus_landlord                |
| 7   | Life off-campus: The security deposit (DP)                       | Student experiences with security deposit disputes and recovery          | https://www.thedp.com/article/2004/01/life_offcampus_the_security_deposit                   |
| 8   | Tips for living with roommates off campus (CU Boulder)           | Peer-informed guide to roommate agreements, utilities, and conflict      | https://www.colorado.edu/studentlife/2023/08/21/tips-living-roommates-campus                |
| 9   | The Dark Side of Off Campus Living (Stanford student resource)   | Student-written survival guide covering safety, landlords, and costs     | https://stanford.edu/~eryilmaz/The_dark_side_of_off_campus_living_and_how_to_avoid_it.html  |
| 10  | What seniors wish they knew before living off-campus (DP)        | Senior students' retrospective advice before their first off-campus year | https://thedp.com/75465010-2d5c-4e4f-8928-c1c44338ea4c                                      |
| 11  | Hidden costs of off-campus living surprise students (DP)         | Students describe unexpected expenses beyond monthly rent                | https://www.thedp.com/article/2011/11/hidden_costs_off_campus_living                        |
| 12  | 7 safety tips to prevent apartment damage — BYU students         | Student-sourced tips on maintenance, mold, and damage prevention         | https://universe.byu.edu/2016/05/13/7-safety-tips-to-prevent-apartment-damage-for-students/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
400 characters

**Overlap:**
100 characters

**Reasoning:**
The corpus has two distinct document types that informed this decision:

_Short-form anecdote and quote documents_ (sources 1-4, 6, 7, 10, 11): The meaningful unit of
information in these is a single student experience - typically a 1-4 sentence around 100–300 characters. A 400-character chunk captures one complete experience
(the student's name or context, their complaint or tip, and any outcome) without merging two
unrelated stories into the same embedding. Keeping chunks at this size means a query like
"what do students say about pest problems?" retrieves a tight, attributable chunk rather than
a paragraph mixing roaches, security deposits, and subletting.

_Long-form guide documents_ (sources 5, 8, 9, 12): These use headers and multi-sentence
paragraphs where one tip might span 2-3 sentences across ~300-600 characters. A 400-character
chunk captures roughly one tip or one sub-section, which is the right area for a user
question about a specific topic like "should I get renters insurance?"

_Why not larger chunks?_ Newspaper articles interleave student quotes from multiple people
about different properties. Chunks larger than ~500 characters start merging separate students'
experiences into one embedding, diluting the semantic signal so that a query about pest
problems returns a chunk that's 60% about maintenance delays and 40% about parking.

_Why not smaller chunks?_ Anything under ~150 characters risks producing fragments like "He
said" or "The landlord eventually" that carry no standalone meaning and would produce near-zero
similarity to any real query.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

Loads locally with `SentenceTransformer("all-MiniLM-L6-v2")`. No API key, no rate limits, no
cost. Produces 384-dimensional dense vectors. Max sequence length is 256 tokens (~1,000
characters), which is well above our 400-character chunk size.

**Top-k:** 5

Starting at k=5 gives the LLM enough context to synthesize an answer across multiple student
experiences (e.g., three different students describing pest problems), without flooding the
prompt with loosely related material. If test queries return too many off-topic chunks, reduce
to 3. If answers are consistently missing obvious information from documents, increase to 7.

**Production tradeoff reflection:**

If deploying this system for real users beyond a class project, I would weigh the following
before choosing an embedding model:

- _Context length:_ all-MiniLM-L6-v2 tops out at 256 tokens. Longer documents or larger
  chunks would require a model with a higher limit, such as `text-embedding-3-small` from
  OpenAI (8,191 tokens) or `nomic-embed-text` (8,192 tokens).

- _Cost:_ all-MiniLM-L6-v2 is free and runs locally. OpenAI's `text-embedding-3-small` is
  priced per token, which matters at scale but is negligible for a small corpus like this.

- _Accuracy on domain-specific text:_ General-purpose models like all-MiniLM-L6-v2 handle
  conversational review text well. For a specialized domain (e.g., legal documents or medical
  records), a domain-fine-tuned model would outperform it.

- _Multilingual support:_ all-MiniLM-L6-v2 is English-only. For a student population where
  users query in other languages, `paraphrase-multilingual-MiniLM-L12-v2` or
  `text-embedding-3-large` would be required.

- _Local vs. API:_ Running locally (sentence-transformers) means no latency from network
  calls and no data leaving the machine, which matters for user privacy. An API model
  introduces per-call latency and sends text to a third party on every query.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                             | Expected answer                                                                                                                                                                                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What do students say about how long landlords take to respond to maintenance issues? | Students report highly variable response times. Some describe same-day or next-day fixes; others describe requests ignored for weeks or months. Penn students at Campus Apartments specifically reported bare-minimum responsiveness, with pest and sewage issues unresolved for extended periods. The consistent advice is to document every request in writing.           |
| 2   | What are the most common reasons students lose their security deposit?               | The most frequently cited reasons are uncleaned appliances (especially stoves and refrigerators), carpet stains, and holes in walls. Property managers note that cleanliness is the single biggest factor. Students should document pre-existing damage at move-in with photos and understand the exact conditions stated in their lease.                                   |
| 3   | What hidden costs beyond rent do students most commonly get surprised by?            | Students most often report being blindsided by separate utility bills (electricity, gas, internet), furniture for unfurnished units, parking fees, and moving costs. Some students described spending hundreds more per month than they budgeted after accounting for these extras.                                                                                         |
| 4   | What advice do students give about signing a lease for the first time?               | Students advise reading the entire lease before signing, paying close attention to renewal clauses (which can allow landlords to raise rent), subletting rules, and security deposit conditions. Several sources recommend using a university's free legal review service. Getting all promises from the landlord in writing not just verbally, is consistently emphasized. |
| 5   | What pest problems do students most commonly report in off-campus apartments?        | Mice and cockroaches are the most frequently reported pests. Penn students at Campus Apartments described mice present on move-in day and sudden roach infestations. Mold is also common, particularly in bathrooms of older buildings, and is worsened by poor ventilation. Students are advised to report any pest issue immediately in writing.                          |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Short student quotes lose attribution context at chunk boundaries.** Many of the
   newspaper articles follow this pattern: a sentence of journalistic framing naming the
   student and their property ("Dominic Weiss, who lived in a Campus Apartments building,
   said that...") immediately followed by the quote. If the chunk splits between the
   attribution sentence and the quote, the retrieved chunk carries the complaint but no
   longer tells the system who said it or about which property, degrading both answer
   accuracy and source attribution.

2. **Thematic overlap across sources may dilute retrieval diversity.** Multiple Daily
   Pennsylvanian articles cover the same sub-topics (landlord complaints, security deposits,
   maintenance). The retrieval system could return 4 of the 5 top-k chunks all from the same
   sub-topic and source, giving the LLM redundant context instead of a range of student
   perspectives.

3. **Vocabulary overlap between landlord and deposit articles causes retrieval
   confusion on maintenance queries.** The security deposit article and the
   landlord advice article share terms like "landlord," "lease," "students,"
   and "apartment," so a query about maintenance response time surfaces deposit
   content as the top result. A potential fix is hybrid search (BM25 + semantic)
   or metadata filtering by sub-topic — noted for the evaluation report.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     ```mermaid

flowchart LR
A["Raw Documents\n(.txt, .pdf files\nin /documents)"]
B["Ingestion & Cleaning\nrequests + BeautifulSoup\npdfplumber for PDFs\nstrip nav, ads, HTML"]
C["Chunking\nRecursiveCharacterTextSplitter\nchunk_size=400\noverlap=100"]
D["Embedding\nall-MiniLM-L6-v2\nsentence-transformers\n384-dim vectors"]
E["Vector Store\nChromaDB (local)\nstores chunk + source\nfilename metadata"]
F["Retrieval\nsemantic similarity search\ntop-k=5\nreturns chunks + sources"]
G["Generation\nGroq llama-3.3-70b-versatile\ngrounded system prompt\nsource citation required"]
H["Query Interface\nGradio web UI\nlocalhost:7860\nanswer + sources displayed"]

    A --> B --> C --> D --> E --> F --> G --> H

```

Five stages in sequence:

- **Document Ingestion:** Load all 12 sources from disk (`.txt` files saved from web scraping
  or manual copy) and one PDF (MIT guide via pdfplumber). Output: a list of
  `{"text": ..., "source": filename}` dicts.

- **Chunking:** Pass each document's text through `RecursiveCharacterTextSplitter`
  (chunk_size=400, overlap=100). Attach the source filename to each chunk as metadata.
  Output: list of chunks with metadata.

- **Embedding + Vector Store:** Embed each chunk with `all-MiniLM-L6-v2` and store in a
  local ChromaDB collection named `"offcampus_housing"` with source metadata. Run once;
  persisted to disk for reuse.

- **Retrieval:** Given a user query, embed it with the same model, run cosine similarity
  search in ChromaDB, return top-5 chunks with source filenames and distance scores.

- **Generation:** Build a prompt from the retrieved chunks, call Groq's
  `llama-3.3-70b-versatile` with a strict grounding instruction, return the answer and a
  list of cited source filenames.

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

*What I will give Claude:* The full Documents table from this file (12 sources, types, URLs),
the Chunking Strategy section (400-char chunks, 100-char overlap, paragraph-first
RecursiveCharacterTextSplitter), and the architecture diagram showing the ingestion stage
labeled "requests + BeautifulSoup, pdfplumber for PDFs."

*What I will ask for:* Implement three functions in `ingest.py`: (1) `load_documents(folder)`
that reads all `.txt` files in `/documents` and returns a list of
`{"text": raw_text, "source": filename}` dicts, (2) `clean_text(text)` that strips HTML tags
using BeautifulSoup, removes blank lines, collapses whitespace, and strips common navigation
boilerplate patterns, and (3) `chunk_documents(docs)` using LangChain's
`RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)` that returns a flat list
of `{"text": chunk, "source": filename}` dicts.

*What I will verify:* I will print one cleaned document before chunking and confirm that
navigation text, HTML entities, and bylines are removed. I will then print 5 random chunks
and verify each is readable, self-contained, and under 400 characters.

**Milestone 3 — Ingestion and chunking:**


**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
```
