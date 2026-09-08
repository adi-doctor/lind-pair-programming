import xml.etree.ElementTree as ET

# Minimal representative C-CDA XML snippet
ccda_sample = """<?xml version="1.0" encoding="UTF-8"?>
<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <realmCode code="US"/>
  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  <templateId root="2.16.840.1.113883.10.20.22.1.1"/>
  <recordTarget>
    <patientRole>
      <id extension="998991" root="2.16.840.1.113883.19.5"/>
      <patient>
        <name>
          <given>Jane</given>
          <family>Doe</family>
        </name>
        <administrativeGenderCode code="F" codeSystem="2.16.840.1.113883.5.1" displayName="Female"/>
        <birthTime value="19840704"/>
      </patient>
    </patientRole>
  </recordTarget>
  <component>
    <structuredBody>
      <!-- Allergies Section (Template ID: 2.16.840.1.113883.10.20.22.2.6.1) -->
      <component>
        <section>
          <templateId root="2.16.840.1.113883.10.20.22.2.6.1"/>
          <code code="48765-2" codeSystem="2.16.840.1.113883.6.1" displayName="Allergies"/>
          <title>ALLERGIES AND ADVERSE REACTIONS</title>
          <entry>
            <act classCode="ACT" moodCode="EVN">
              <entryRelationship typeCode="SUBJ">
                <observation classCode="OBS" moodCode="EVN">
                  <participant typeCode="CSM">
                    <participantRole classCode="MANU">
                      <playingEntity classCode="MMAT">
                        <code code="70618" displayName="Penicillin" codeSystem="2.16.840.1.113883.6.88"/>
                      </playingEntity>
                    </participantRole>
                  </participant>
                </observation>
              </entryRelationship>
            </act>
          </entry>
        </section>
      </component>
    </structuredBody>
  </component>
</ClinicalDocument>
"""

# Define the C-CDA namespace map
NS = {
    'cda': 'urn:hl7-org:v3'
}

"""
Clinical                    DomainTemplate ID (root)                LOINC Section Code
--------                    ------------------------                ------------------
Allergies & Intolerances    2.16.840.1.113883.10.20.22.2.6.1        48765-2
Medications                 2.16.840.1.113883.10.20.22.2.1.1        10160-0
Problem List                2.16.840.1.113883.10.20.22.2.5.1        11450-4
Results / Labs              2.16.840.1.113883.10.20.22.2.3.1        30954-2
Vital Signs                 2.16.840.1.113883.10.20.22.2.4.1        8716-3
Immunizations               2.16.840.1.113883.10.20.22.2.2.1        11369-6
"""

def parse_ccda(xml_data: str):
    root = ET.fromstring(xml_data)

    # 1. Extract Patient Demographics
    patient_node = root.find('.//cda:recordTarget/cda:patientRole/cda:patient', NS)

    first_name = patient_node.findtext('cda:name/cda:given', default='', namespaces=NS)
    last_name = patient_node.findtext('cda:name/cda:family', default='', namespaces=NS)

    gender_node = patient_node.find('cda:administrativeGenderCode', NS)
    gender = gender_node.attrib.get('displayName') if gender_node is not None else 'Unknown'

    birth_time_node = patient_node.find('cda:birthTime', NS)
    dob = birth_time_node.attrib.get('value') if birth_time_node is not None else 'Unknown'

    print(f"Patient: {first_name} {last_name}")
    print(f"DOB: {dob} | Gender: {gender}\n")

    # 2. Extract Sections by Template ID
    # Allergies template root: 2.16.840.1.113883.10.20.22.2.6.1
    allergies_section = None
    for section in root.findall(".//cda:section", NS):
        template_id = section.find("cda:templateId[@root='2.16.840.1.113883.10.20.22.2.6.1']", NS)
        if template_id is not None:
            allergies_section = section
            break

    if allergies_section is not None:
        title = allergies_section.findtext('cda:title', default='Allergies', namespaces=NS)
        print(f"--- {title} ---")

        # Search for allergy substances inside participant/playingEntity nodes
        substances = allergies_section.findall(
            ".//cda:participant[@typeCode='CSM']//cda:playingEntity/cda:code",
            NS
        )
        for s in substances:
            substance_name = s.attrib.get('displayName')
            code = s.attrib.get('code')
            print(f"- Allergen: {substance_name} (RxNorm: {code})")


parse_ccda(ccda_sample)

"""
Third-Party Libraries
For full C-CDA ingestion, consider open-source converters rather than writing raw XPath parsers for every edge case:

FHIR Converters: Microsoft's open-source FHIR-Converter converts C-CDA XML to FHIR JSON resources via Liquid templates.

pyhealth / hl7apy: Can parse or structure health data, though they are primarily HL7 v2 focused.

lxml: Preferred over standard library xml.etree for high-volume C-CDA parsing due to speed and native XPath 1.0 support (root.xpath("//cda:section[...]", namespaces=NS)).
"""