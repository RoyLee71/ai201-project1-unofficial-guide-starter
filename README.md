# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

     Off-campus housing is one of the most consequential decisions a college student makes, yet the information they need most like: how landlords actually respond to maintenance requests, which lease clauses cause problems, what hidden costs to expect; lives almost entirely in student conversations, newspaper threads, and Reddit posts rather than in anything a university publishes. Official housing pages list available properties but don't tell which landlords ignore mold complaints for six months or that your deposit disappears if you miss a cleaning clause buried on page 4 of the lease. This system makes that hard-won peer knowledge searchable and answerable.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters

**Overlap:** 100 characters

**Why these choices fit your documents:**

The corpus has two distinct document types. Short-form anecdote and quote
documents (Daily Pennsylvanian articles, BYU horror stories) contain the
meaningful unit of information in 1–4 sentence student quotes, typically
100–300 characters each. A 400-character chunk captures one complete student
experience; name, complaint, and outcome; without merging two unrelated
stories into the same embedding.

Long-form guide documents (Stanford dark side, CU Boulder roommate tips) use
multi-sentence paragraphs where one tip spans ~300–500 characters. The
400-character limit captures roughly one tip per chunk, which is the right
range for specific user questions.

The 100-character overlap (25%) prevents key attribution context; for example,
a student's name or property name at the end of one chunk, from being
separated from the follow-on sentence containing their actual complaint.
Paragraph-based splitting (`\n\n`) is attempted first, with a fallback to
fixed-size splitting using LangChain's `RecursiveCharacterTextSplitter`.

**Final chunk count:** 155

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

Loads locally with `SentenceTransformer("all-MiniLM-L6-v2")`. No API key,
no rate limits, no cost. Produces 384-dimensional dense vectors with a
256-token maximum sequence length, comfortably above the 400-character chunk
size used in this project.

**Production tradeoff reflection:**

For a real deployment I would weigh four factors when choosing a different
model. Context length: all-MiniLM-L6-v2 tops out at 256 tokens, which works
for short review text but would fail on longer documents like full lease
agreements; text-embedding-3-small from OpenAI supports 8,191 tokens. Cost:
all-MiniLM-L6-v2 is free and runs locally, while API-based models charge per
token, which matters at scale. Multilingual support: this model is
English-only; a student population querying in other languages would require
paraphrase-multilingual-MiniLM-L12-v2 or similar. Privacy: running locally
means no text leaves the machine on each query, which matters if users are
submitting sensitive information about their housing situations.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
You are an assistant that helps college students understand off-campus housing

experiences based exclusively on real student accounts.
STRICT RULES:

Answer ONLY using the information in the provided documents below.
Do NOT use any outside knowledge, general advice, or your training data.
If the documents do not contain enough information to answer the question,

respond with exactly: "I don't have enough information on that in my

documents." Do NOT append a Sources line when declining.
Always cite which document(s) your answer draws from at the end of your

response, using the format: Sources: [filename1, filename2]
List each source filename only ONCE, even if you drew from it multiple times.
Be specific and quote or closely paraphrase the student experiences in the

documents.
Do not make up details, statistics, or experiences not present in the

documents.

**How source attribution is surfaced in the response:**
Source attribution is enforced two ways. First, the system prompt instructs
the LLM to append a `Sources:` line naming each document it drew from. Second,
the `ask()` function in `query.py` programmatically collects the unique source
filenames from the top-k retrieved chunks and returns them in the `sources`
key of the response dict, which the Gradio interface displays in a separate
`Retrieved from` box. This means attribution appears even if the LLM omits
it from the answer text.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| 1 | What do students say about landlord response time for maintenance? | Variable — some same-day, others weeks; document everything in writing | Only Friedman's positive experience presented landlord responds "almost always immediately"| Partially relevant | Partially accurate |
| 2 | What are the most common reasons students lose their security deposit? | Uncleaned appliances, carpet stains, holes in walls; cleanliness is the main factor | Correctly identifies uncleaned appliances, carpet damage, repainting walls, staining furniture | Relevant | Accurate |
| 3 | What hidden costs beyond rent do students get surprised by? | Utilities, furniture, parking, moving costs | Covers utilities and furniture correctly; mentions "room view" as a cost; misses parking and moving costs | Relevant | Partially accurate|
| 4 | What advice do students give about signing a lease for the first time? | Read the full lease, watch renewal clauses, get everything in writing, use free legal review | Advises checklist and speaking up during tours; misses renewal clauses, reading the lease fully, and legal review services | Partially relevant | Partially accurate |
| 5 | What pest problems do students most commonly report in off-campus apartments? | Mice, cockroaches, mold; often ignored for extended periods | Identifies bug infestations and rodent problems with Weiss quote; misses cockroaches by name, mold entirely, and the pattern of being ignored | Relevant | Partially accurate |
**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What do students say about landlord response time for maintenance?

**What the system returned:**
The top retrieved chunk came from `dp_security_deposit.txt` (distance 0.4517)
rather than from the landlord advice article. The answer was partially correct
because the second-ranked chunk from `dp_landlord_advice.txt` contained a
relevant quote, but the LLM had to work around an irrelevant top result.

**Root cause (tied to a specific pipeline stage):**
This is a retrieval failure rooted in vocabulary overlap between documents.
In the chunking and embedding stage, the security deposit article and the
landlord advice article share high-frequency terms; landlord, lease,
apartment, students, problems, so their embeddings are semantically close
even though they cover different sub-topics. The all-MiniLM-L6-v2 model
embeds based on overall vocabulary similarity rather than topic specificity,
and at this corpus size (155 chunks from 10 documents) there isn't enough
distinction between the two documents' embeddings to separate them cleanly.

**What you would change to fix it:**
First, add sub-topic metadata (e.g., tagging each chunk as
"maintenance," "deposits," "costs") during the chunking stage and filtering
by metadata tag before running similarity search, this is the metadata
filtering stretch feature. Second, use hybrid search combining BM25 keyword
matching with semantic search: a keyword query for "maintenance response time"
would heavily favor the landlord advice article over the deposit article
because "maintenance" appears far more frequently there.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

Writing the chunking strategy section before touching any code forced a
concrete decision about chunk size before seeing the actual output. When
ingest.py produced chunks that included HTML artifacts and encoding errors,
the spec gave a clear target; 400-character, self-contained chunks to
evaluate against. Without it, "is this chunk good enough?" would have been
subjective. With the spec, the answer was mechanical: does this chunk make
sense on its own and sit under 400 characters?

**One way your implementation diverged from the spec, and why:**

The spec anticipated 80–150 chunks. The actual count was 155, slightly above
the upper estimate. This happened because several Daily Pennsylvanian articles
were longer than the average 2,000-character estimate used in the spec
`dp_landlord_issues_2024.txt` alone was 8,307 characters, producing
significantly more chunks than planned. The chunk size and overlap were kept
at the specified values because the validation sample showed clean,
self-contained chunks, the higher count was a corpus size underestimate, not
a chunking problem.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_ The Documents section of planning.md (12 sources with
  URLs and types), the Chunking Strategy section (400-char chunks, 100-char
  overlap, paragraph-first RecursiveCharacterTextSplitter), and the
  architecture diagram.
- _What it produced:_ `load_documents()`,
  `clean_text()`, and `chunk_documents()` functions in my ingest.py, plus a `collect_documents.py`
  scraper.
- _What I changed or overrode:_ The `clean_text()` function didn't initially
  handle UTF-8 encoding artifacts (smart quotes and em-dashes rendering as `â`).
  I added explicit unicode replacement lines after discovering the artifact in
  a sample chunk from `stanford_dark_side.txt`. I also added a minimum chunk
  length filter (`len > 20`) that wasn't in the generated code, after seeing
  near-empty fragments in early test runs.

**Instance 2**

- _What I gave the AI:_ The Retrieval Approach section of planning.md
  (all-MiniLM-L6-v2, ChromaDB, top-k=5), the architecture diagram, and the
  grounding requirement (answers only from retrieved context, source citation
  required in every response).
- _What it produced:_ `retrieval.py` with `build_index()` and
  `retrieve()` functions, and `query.py` with `ask()`.
- _What I changed or overrode:_ The initial system prompt used soft language
  ("try to use the provided documents") which caused the LLM to occasionally
  draw on general knowledge. I rewrote it to use strict prohibitive language
  ("It is strictly forbidden to use any information outside the provided
  documents").
