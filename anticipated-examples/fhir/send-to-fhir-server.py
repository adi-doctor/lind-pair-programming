import requests

fhir_server_base = "https://hapi.fhir.org/baseR4"

response = requests.post(
    f"{fhir_server_base}/Patient",
    data=patient.json(),
    headers={"Content-Type": "application/fhir+json"}
)

if response.status_code in (200, 201):
    created_resource = response.json()
    print(f"Created on server with ID: {created_resource.get('id')}")
else:
    print(f"Failed ({response.status_code}): {response.text}")