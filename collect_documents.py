# collect_documents.py
# Run once to download all web sources into /documents
import requests
from bs4 import BeautifulSoup
import os, time, json

DOCUMENTS_DIR = "documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (educational project)"}

WEB_SOURCES = {
    "dp_landlord_issues_2024.txt":  "https://www.thedp.com/article/2024/03/penn-off-campus-housing-landlord-issues",
    "byu_horror_stories.txt":       "https://universe.byu.edu/2017/08/22/students-share-their-housing-horror-stories/",
    "dp_housing_weird.txt":         "https://www.thedp.com/article/2015/10/when-housing-gets-weird",
    "dp_landlord_advice.txt":       "https://www.thedp.com/article/2005/02/how_to_work_with_an_offcampus_landlord",
    "dp_security_deposit.txt":      "https://www.thedp.com/article/2004/01/life_offcampus_the_security_deposit",
    "cu_roommate_tips.txt":         "https://www.colorado.edu/studentlife/2023/08/21/tips-living-roommates-campus",
    "stanford_dark_side.txt":       "https://stanford.edu/~eryilmaz/The_dark_side_of_off_campus_living_and_how_to_avoid_it.html",
    "dp_seniors_advice.txt":        "https://thedp.com/75465010-2d5c-4e4f-8928-c1c44338ea4c",
    "dp_hidden_costs.txt":          "https://www.thedp.com/article/2011/11/hidden_costs_off_campus_living",
    "byu_safety_tips.txt":          "https://universe.byu.edu/2016/05/13/7-safety-tips-to-prevent-apartment-damage-for-students/",
}

def scrape_article(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove nav, footer, scripts, styles, ads
    for tag in soup(["nav", "footer", "script", "style", "aside",
                     "header", "form", "button", "iframe"]):
        tag.decompose()

    # Try article body first, fall back to main, then body
    content = (soup.find("article") or
               soup.find("main") or
               soup.find(class_=["article-body", "entry-content", "post-content"]) or
               soup.find("body"))

    return content.get_text(separator="\n", strip=True) if content else ""

# --- Scrape web articles ---
for filename, url in WEB_SOURCES.items():
    out_path = os.path.join(DOCUMENTS_DIR, filename)
    if os.path.exists(out_path):
        print(f"  Already exists, skipping: {filename}")
        continue
    try:
        print(f"Fetching {filename}...")
        text = scrape_article(url)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  Saved: {len(text)} characters")
        time.sleep(1)  # be polite
    except Exception as e:
        print(f"  FAILED {filename}: {e}")
        print(f"  --> Copy this page manually to documents/{filename}")

# --- Reddit via JSON API (no login required) ---
reddit_out = os.path.join(DOCUMENTS_DIR, "reddit_offcampus_posts.txt")
if not os.path.exists(reddit_out):
    print("Fetching Reddit posts...")
    try:
        url = "https://www.reddit.com/r/college/search.json?q=off+campus+housing&restrict_sr=1&sort=top&limit=25"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        posts = data["data"]["children"]
        lines = []
        for post in posts:
            p = post["data"]
            title = p.get("title", "")
            body  = p.get("selftext", "")
            if body and body != "[removed]" and body != "[deleted]":
                lines.append(f"POST: {title}\n{body}\n")
        with open(reddit_out, "w", encoding="utf-8") as f:
            f.write("\n---\n".join(lines))
        print(f"  Saved {len(posts)} Reddit posts")
    except Exception as e:
        print(f"  Reddit fetch failed: {e}")
        print("  --> Manually copy 10–15 Reddit posts to documents/reddit_offcampus_posts.txt")