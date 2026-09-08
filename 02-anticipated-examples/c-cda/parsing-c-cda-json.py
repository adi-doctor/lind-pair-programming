import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional

# Standard C-CDA OID to FHIR System URI map
OID_MAP = {
    "2.16.840.1.113883.6.88": "http://www.nlm.nih.gov/research/umls/rxnorm",
    "2.16.840.1.113883.6.96": "http://snomed.info/sct",
    "2.16.840.1.113883.6.1": "http://loinc.org",
    "2.16.840.1.113883.5.1": "http://hl7.org/fhir/administrative-gender"
}

GENDER_MAP = {
    "M": "male",
    "F": "female",
    "UN": "unknown"
}

NS = {"cda": "urn:hl7-org:v3"}


def parse_cda_date(cda_date_str: Optional[str]) -> Optional[str]:
    """Convert C-CDA timestamp (YYYYMMDD...) to FHIR ISO format."""
    if not cda_date_str:
        return None
    cleaned = cda_date_str[:8]
    try:
        dt = datetime.strptime(cleaned, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def extract_patient(root: ET.Element) -> Dict[str, Any]:
    """Maps C-CDA recordTarget to FHIR Patient resource."""
    patient_role = root.find(".//cda:recordTarget/cda:patientRole", NS)
    patient_elem = patient_role.find("cda:patient", NS) if patient_role is not None else None

    if patient_elem is None:
        return {}

    # Extract ID
    id_elem = patient_role.find("cda:id", NS)
    patient_id = id_elem.attrib.get("extension", "unknown-patient") if id_elem is not None else "unknown-patient"

    # Extract Name
    first_name = patient_elem.findtext("cda:name/cda:given", default="", namespaces=NS)
    last_name = patient_elem.findtext("cda:name/cda:family", default="", namespaces=NS)

    # Extract Gender
    gender_code = patient_elem.find("cda:administrativeGenderCode", NS)
    gender_val = gender_code.attrib.get("code") if gender_code is not None else None
    fhir_gender = GENDER_MAP.get(gender_val, "unknown")

    # Extract DOB
    birth_time = patient_elem.find("cda:birthTime", NS)
    birth_date = parse_cda_date(birth_time.attrib.get("value")) if birth_time is not None else None

    return {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [{
            "use": "official",
            "family": last_name,
            "given": [first_name] if first_name else []
        }],
        "gender": fhir_gender,
        "birthDate": birth_date
    }


def extract_medications(root: ET.Element, patient_ref: str) -> List[Dict[str, Any]]:
    """
    Maps C-CDA Medications section (Template: 2.16.840.1.113883.10.20.22.2.1.1)
    to FHIR MedicationRequest resources.
    """
    medications = []

    # Locate C-CDA Medication section
    med_section = None
    for section in root.findall(".//cda:section", NS):
        template_id = section.find("cda:templateId[@root='2.16.840.1.113883.10.20.22.2.1.1']", NS)
        if template_id is not None:
            med_section = section
            break
    if med_section is None:
        return medications

    # Find all substanceAdministration entries
    sub_admins = med_section.findall(".//cda:substanceAdministration", NS)
    for idx, admin in enumerate(sub_admins):
        # Extract ID
        admin_id_elem = admin.find("cda:id", NS)
        med_id = admin_id_elem.attrib.get("extension",
                                          f"med-{idx + 1}") if admin_id_elem is not None else f"med-{idx + 1}"

        # Extract status
        status_code = admin.find("cda:statusCode", NS)
        status_val = status_code.attrib.get("code", "completed") if status_code is not None else "completed"
        fhir_status = "active" if status_val == "active" else "completed"

        # Extract consumable medication code
        cons_code = admin.find(".//cda:consumable//cda:manufacturedProduct//cda:code", NS)
        med_concept = {}
        if cons_code is not None:
            code = cons_code.attrib.get("code")
            display = cons_code.attrib.get("displayName")
            system_oid = cons_code.attrib.get("codeSystem")
            system_uri = OID_MAP.get(system_oid, f"urn:oid:{system_oid}")

            med_concept = {
                "coding": [{
                    "system": system_uri,
                    "code": code,
                    "display": display
                }],
                "text": display
            }

        # Build FHIR MedicationRequest
        med_request = {
            "resourceType": "MedicationRequest",
            "id": med_id,
            "status": fhir_status,
            "intent": "order",
            "medicationCodeableConcept": med_concept,
            "subject": {
                "reference": f"Patient/{patient_ref}"
            }
        }
        medications.append(med_request)

    return medications


def ccda_to_fhir_bundle(ccda_xml_str: str) -> Dict[str, Any]:
    """Parses C-CDA and bundles resources into a FHIR collection."""
    root = ET.fromstring(ccda_xml_str)

    patient = extract_patient(root)
    patient_id = patient.get("id", "patient-1")
    meds = extract_medications(root, patient_ref=patient_id)

    bundle_entries = []
    if patient:
        bundle_entries.append({
            "fullUrl": f"urn:uuid:{patient_id}",
            "resource": patient
        })

    for med in meds:
        bundle_entries.append({
            "fullUrl": f"urn:uuid:{med['id']}",
            "resource": med
        })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": bundle_entries
    }


# Sample C-CDA XML with Demographics and a Medication entry
sample_cda = """<?xml version="1.0" encoding="UTF-8"?>
<ClinicalDocument xmlns="urn:hl7-org:v3">
  <recordTarget>
    <patientRole>
      <id extension="P-55201" root="2.16.840.1.113883.19.5"/>
      <patient>
        <name>
          <given>Robert</given>
          <family>Chen</family>
        </name>
        <administrativeGenderCode code="M" codeSystem="2.16.840.1.113883.5.1" displayName="Male"/>
        <birthTime value="19750315"/>
      </patient>
    </patientRole>
  </recordTarget>
  <component>
    <structuredBody>
      <component>
        <section>
          <!-- Medication Section Template ID -->
          <templateId root="2.16.840.1.113883.10.20.22.2.1.1"/>
          <code code="10160-0" codeSystem="2.16.840.1.113883.6.1" displayName="History of Medication Use"/>
          <title>Medications</title>
          <entry>
            <substanceAdministration classCode="SBADM" moodCode="EVN">
              <id extension="MED-RX-9821" root="2.16.840.1.113883.19"/>
              <statusCode code="active"/>
              <consumable>
                <manufacturedProduct classCode="MANU">
                  <manufacturedMaterial>
                    <code code="860975" codeSystem="2.16.840.1.113883.6.88" displayName="Lisinopril 10 MG Oral Tablet"/>
                  </manufacturedMaterial>
                </manufacturedProduct>
              </consumable>
            </substanceAdministration>
          </entry>
        </section>
      </component>
    </structuredBody>
  </component>
</ClinicalDocument>
"""

fhir_bundle = ccda_to_fhir_bundle(sample_cda)
print(json.dumps(fhir_bundle, indent=2))

"""
Executing the script generates standard JSON compliant with the FHIR R4 specifications:

{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "fullUrl": "urn:uuid:P-55201",
      "resource": {
        "resourceType": "Patient",
        "id": "P-55201",
        "name": [
          {
            "use": "official",
            "family": "Chen",
            "given": [
              "Robert"
            ]
          }
        ],
        "gender": "male",
        "birthDate": "1975-03-15"
      }
    },
    {
      "fullUrl": "urn:uuid:MED-RX-9821",
      "resource": {
        "resourceType": "MedicationRequest",
        "id": "MED-RX-9821",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
          "coding": [
            {
              "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
              "code": "860975",
              "display": "Lisinopril 10 MG Oral Tablet"
            }
          ],
          "text": "Lisinopril 10 MG Oral Tablet"
        },
        "subject": {
          "reference": "Patient/P-55201"
        }
      }
    }
  ]
}

"""