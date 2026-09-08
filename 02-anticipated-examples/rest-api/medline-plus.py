import json
import requests

# Base endpoint for MedlinePlus Connect
url = "https://connect.medlineplus.gov/service"

# Query parameters for Type 2 Diabetes (ICD-10-CM: E11.9)
params = {
    "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.90",  # ICD-10-CM OID
    "mainSearchCriteria.v.c": "E11.9",                     # Diagnosis code
    "knowledgeResponseType": "application/json",           # Request JSON output
    "informationRecipient.languageCode.c": "en"            # Language
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # The returned feed structure contains entry summaries
    feed = data.get("feed", {})
    entries = feed.get("entry", [])

    for entry in entries:
        title = entry.get("title", {}).get("_value")
        # Summary contains HTML-formatted definition and overview
        summary = entry.get("summary", {}).get("_value")
        link = entry.get("link", [{}])[0].get("href")

        print(f"Title: {title}")
        print(f"URL: {link}")
        print(f"Summary Snippet:\n{summary[:300]}...\n")

except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")