import json
import requests

## uvicorn main:app --reload
# Control C to stop the server.

# 1. Target API endpoint (returns sample JSON data)
# url = "https://jsonplaceholder.typicode.com/posts/1"
# url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
# url = "https://api.fda.gov/"
url = "http://localhost:8000/items/1"

try:
    # 2. Send GET request to the API
    response = requests.get(url, timeout=10)

    # 3. Raise an exception for HTTP error codes (4xx, 5xx)
    response.raise_for_status()

    # 4. Parse the JSON response into a Python object (dictionary)
    data = response.json()

    # 5. Serialize the Python object into a formatted JSON string
    formatted_json = json.dumps(data, indent=4)

    # 6. Print the output
    print("API Response Output:")
    print(formatted_json)

except requests.exceptions.RequestException as error:
    print(f"Request failed: {error}")