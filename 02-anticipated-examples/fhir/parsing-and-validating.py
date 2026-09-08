from fhir.resources.patient import Patient

raw_fhir_data = {
    "resourceType": "Patient",
    "id": "12345",
    "gender": "male",
    "birthDate": "1985-11-20",
    "name": [
        {
            "family": "Smith",
            "given": ["John"]
        }
    ]
}

# Parse and validate dictionary / JSON
patient_obj = Patient.model_validate(raw_fhir_data)

print(f"Loaded Patient: {patient_obj.name[0].family}, ID: {patient_obj.id}")