import html
import requests
import json
import re

condition = "bladder-cancer"
url = f"https://medlineplus.gov/download/genetics/condition/{condition}.json"
print("API Url: " + url)
headers = {
    "User-Agent": "MyMedicalApp/1.0 (andrew@adi.doctor)"
}
response = requests.get(url, headers=headers, timeout=10)

# Helper function to strip HTML tags into clean text
def clean_html(raw_html: str) -> str:
    unescaped = html.unescape(raw_html)
    cleaned = re.sub(r"<[^>]+>", " ", unescaped)
    return " ".join(cleaned.split())

if response.status_code == 200:
    data = response.json()
    # print(data)
    name = data.get("name")

    # 1. Basic Metadata
    condition_name = data.get("name")
    ghr_page = data.get("ghr_page")
    last_reviewed = data.get("reviewed")

    # 2. Extract and Clean HTML Description
    description_html = ""
    for item in data.get("text-list", []):
        text_obj = item.get("text", {})
        if text_obj.get("text-role") == "description":
            description_html = text_obj.get("html", "")
            break
    clean_description = clean_html(description_html)

    # 3. Flatten Synonyms
    synonyms = [item["synonym"] for item in data.get("synonym-list", []) if "synonym" in item]

    # 4. Extract Inheritance Patterns
    inheritance = [
        item["inheritance-pattern"]["memo"]
        for item in data.get("inheritance-pattern-list", [])
        if "inheritance-pattern" in item
    ]

    # 5. Extract Related Genes (Symbol and URL)
    genes = [
        item["related-gene"]["gene-symbol"]
        for item in data.get("related-gene-list", [])
        if "related-gene" in item
    ]

    # 6. Group Database Cross-References by DB type (ICD-10, OMIM, SNOMED, etc.)
    db_references = {}
    for item in data.get("db-key-list", []):
        db_entry = item.get("db-key", {})
        db_name = db_entry.get("db")
        db_key = db_entry.get("key")
        if db_name and db_key:
            db_references.setdefault(db_name, []).append(db_key)

    # Display parsed results
    print(f"Condition: {condition_name} (Reviewed: {last_reviewed})")
    print(f"Webpage:   {ghr_page}")
    print(f"\nDescription:\n{clean_description}")
    print(f"\nInheritance Patterns: {', '.join(inheritance)}")
    print(f"Total Genes Associated: {len(genes)} (e.g., {', '.join(genes[:5])}...)")
    print(f"Synonyms ({len(synonyms)}): {synonyms[:3]}...")
    print("\nCross-References:")
    for db, keys in db_references.items():
        print(f"  - {db}: {', '.join(keys)}")
    # html = data.get("list")  # Get the HTML content
    # print(f"Condition: {name}")
    # print(f"Definition:\n{html}")
    # The MedlinePlus response contains nested structures such as HTML descriptions, gene mappings, database identifiers, and inheritance patterns.

else:
    print(f"Failed to fetch data: HTTP {response.status_code}")