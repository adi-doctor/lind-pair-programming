import pandas as pd
import hl7
from tabulate import tabulate

def parse_hl7_to_dataframe(hl7_data):
    """
    Parses HL7 data and converts it into a pandas DataFrame.
    """
    try:
        # Parse the HL7 message
        h = hl7.parse(hl7_data)

        # Extract patient information
        patient_id = str(h.segment('PID')[2])
        patient_name = str(h.segment('PID')[5])
        patient_dob = str(h.segment('PID')[7])

        # Extract observation results
        observations = []
        for obs in h.segments('OBX'):
            observation_id = str(obs[3])
            observation_value = str(obs[5])
            observation_units = str(obs[6])
            observation_datetime = str(obs[14])
            observations.append([observation_id, observation_value, observation_units, observation_datetime])

        # Create a DataFrame for observations
        if observations:
            df = pd.DataFrame(observations, columns=['Observation ID', 'Value', 'Units', 'DateTime'])
            df['Patient ID'] = patient_id
            df['Patient Name'] = patient_name
            df['Patient DOB'] = patient_dob
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        print(f"Error parsing HL7 message: {e}")
        return None

def tabulate_example_using_dictionary():
    # Keys and headers for the DataFrame
    users = [
        {"ID": 101, "Username": "jdoe", "Active": True},
        {"ID": 102, "Username": "asmith", "Active": False},
        {"ID": 103, "Username": "bwayne", "Active": True},
    ]
    headers = ["ID", "Username", "Active"]
    df = pd.DataFrame(users, columns=headers)
    print(tabulate(df, headers='keys'))

def create_hl7_file():
    # HL7 v2 standard requires carriage return (\r) as the segment delimiter
    hl7_content = "\r".join([
        r"MSH|^~\&|EPIC|HOSPITAL|LAB|CLINIC|20260906120000||ADT^A01|MSG00001|P|2.5",
        r"EVN|A01|20260906120000",
        r"PID|1||10006789^^^HOSPITAL^MR||DOE^JOHN^A||19850412|M|||123 MAIN ST^^NEWPORT BEACH^CA^92660||555-123-4567|||S",
        r"PV1|1|I|ICU^01^01|E|||12345^SMITH^ALICE^MD|||MED||||||||ADM|20260906113000",
    ]) + "\r"
    with open("sample_message.hl7", "w", encoding="utf-8") as f:
        f.write(hl7_content)
    print("Saved sample_message.hl7 successfully.")

def ingest_hl7():
    with open("sample_message.hl7", "r", encoding="utf-8") as f:
        raw_message = f.read()
    print(str(raw_message))
    # splitlines() handles \r, \n, and \r\n cleanly
    segments = raw_message.splitlines()
    parsed_dict = {}
    for line in segments:
        line = line.strip()
        if not line:
            continue
        fields = line.split("|")
        segment_name = fields[0].strip()
        if segment_name == "PID":
            name_components = fields[5].split("^")
            parsed_dict["last_name"] = name_components[0] if len(name_components) > 0 else ""
            parsed_dict["first_name"] = name_components[1] if len(name_components) > 1 else ""
            parsed_dict["dob"] = fields[7] if len(fields) > 7 else ""
            parsed_dict["mrn"] = fields[3].split("^")[0] if len(fields) > 3 else ""
    print("Found segments:", [line.split("|")[0] for line in segments if line.strip()])
    print("Parsed PID:", parsed_dict)


if __name__ == '__main__':
    # Example HL7 v2.5 message
    hl7_message = (
        "MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|202301011200||ORU^R01|MSG00001|P|2.5\r"
        "PID|1||12345^^^MRN|ALT_ID|Doe^John^^^|Mother's Maiden Name|19700101|M|||123 Main St^^Anytown^CA^12345||(555)555-5555|||S|||123456789|SSN\r"
        "OBR|1|ORDER_ID|FILLER_ORDER_ID|UNIVERSAL_SERVICE_ID^Test^L|||202301011200|||||||||||202301011200|||F\r"
        "OBX|1|NM|GLUCOSE^Glucose^L|1|100|mg/dL|70-110|N|||F|||202301011200\r"
        "OBX|2|NM|CREATININE^Creatinine^L|1|1.2|mg/dL|0.6-1.3|N|||F|||202301011200\r"
    )

    # Parse the HL7 message and create a DataFrame
    df = parse_hl7_to_dataframe(hl7_message)

    if df is not None and not df.empty:
        print("HL7 data successfully converted to pandas DataFrame:")
        print(df)

    # Display the DataFrame in a tabular format
    print("\nHL7 Data in Tabular Format:")
    print(tabulate(df, headers='keys', tablefmt='grid'))

    # create_hl7_file()
    ingest_hl7()

