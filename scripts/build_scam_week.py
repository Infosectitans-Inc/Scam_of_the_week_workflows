import json, datetime, feedparser, html, re, os

SOURCES = [
    {"name": "FTC", "url": "https://www.ftc.gov/rss/consumer-alerts.xml"},
    {"name": "FBI IC3", "url": "https://www.ic3.gov/Media/News/Atom.aspx"},
    {"name": "CISA", "url": "https://www.cisa.gov/news.xml"},
]

OUT_DIR = "content"

def clean(text: str, max_len=600):
    if not text:
        return ""
    # strip HTML tags crudely and unescape entities
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:max_len].rstrip()

def fetch_entries():
    items = []
    for src in SOURCES:
        feed = feedparser.parse(src["url"])
        for e in feed.entries[:10]:
            items.append({
                "src": src["name"],
                "title": getattr(e, "title", "").strip(),
                "summary_raw": getattr(e, "summary", "") or getattr(e, "subtitle", ""),
                "link": getattr(e, "link", ""),
                "published": getattr(e, "published", "") or getattr(e, "updated", ""),
            })
    # most recent first where we have a title + link
    items = [i for i in items if i["title"] and i["link"]]
    items.sort(key=lambda x: x["published"], reverse=True)
    return items

def make_item(entry):
    today = datetime.date.today()
    iso = today.isocalendar()
    week_id = f"{iso[0]}-W{iso[1]:02d}"
    return {
        "id": week_id,
        "week_of": str(today),
        "title": entry["title"],
        "summary": clean(entry["summary_raw"]) or "Key consumer scam alert summarized for this week.",
        "red_flags": [
            "Unsolicited contact asking for personal/financial info",
            "Urgent language or threats (account locked, legal action)",
            "Links or attachments from unknown senders"
        ],
        "what_to_do": [
            "Do not click links—go directly to the official website/app",
            "Never share passwords, 2FA codes, or full SSN",
            "Report to the FTC at reportfraud.ftc.gov and your bank"
        ],
        "sources": [{"name": entry["src"], "url": entry["link"]}],
        "hero_image": ""
    }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    entries = fetch_entries()
    if not entries:
        raise SystemExit("No feed entries found.")
    item = make_item(entries[0])
    payload = {
        "version": 1,
        "updated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "items": [item],
    }

    with open(os.path.join(OUT_DIR, "scam-of-the-week.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Also write a versioned single-file artifact for the archive/rollback
    with open(os.path.join(OUT_DIR, f"{item['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)

if __name__ == "__main__":
    main()
