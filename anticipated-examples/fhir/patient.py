import json
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier

# 1. Build child components
patient_name = HumanName(
    use="official",
    family="Doe",
    given=["Jane", "Marie"],
    prefix=["Ms."]
)

telecom_email = ContactPoint(
    system="email",
    value="jane.doe@example.com",
    use="home"
)

home_address = Address(
    use="home",
    line=["123 Health Ave"],
    city="Boston",
    state="MA",
    postalCode="02115",
    country="USA"
)

mrn_identifier = Identifier(
    system="http://hospital.example.org/mrn",
    value="MRN-987654"
)

# 2. Construct the root Patient resource
patient = Patient(
    id="example-patient-001",
    active=True,
    identifier=[mrn_identifier],
    name=[patient_name],
    telecom=[telecom_email],
    gender="female",
    birthDate="1990-05-14",
    address=[home_address]
)

# 3. Export to FHIR-compliant JSON
patient_json = patient.json(indent=2)
print(patient_json)