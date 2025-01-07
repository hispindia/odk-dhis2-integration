import requests
from constants import ODK_API_URL, ODK_AUTH, DHIS2_API_URL, DHIS2_AUTH, LOG_FILE, PROGRAM_STAGE_ID
from utils import configure_logging
from mapping import map_odk_to_dhis2
from integration import get_dhis2_orgunit_uid_by_nin, data_value_exists_in_dhis2, create_tracker_payload, push_to_dhis2
import logging

def main():
    configure_logging(LOG_FILE)
    session = requests.Session()
    session.auth = DHIS2_AUTH

    # Load the data element mapping
    program_stage_url = f"{DHIS2_API_URL}/programStages/{PROGRAM_STAGE_ID}?fields=programStageDataElements[dataElement[id,name,code]]"
    response = session.get(program_stage_url)
    if response.status_code == 200:
        program_stage_data = response.json()
        calculate_element_mapping = {
            element['dataElement']['name']: element['dataElement']['id']
            for element in program_stage_data['programStageDataElements']
            if 'calculate' in element['dataElement']['code']
        }
        non_calculate_element_mapping = {
            element['dataElement']['code']: element['dataElement']['id']
            for element in program_stage_data['programStageDataElements']
            if 'calculate' not in element['dataElement']['code']
        }
    else:
        logging.error(f"Failed to fetch program stage data. Status code: {response.status_code}")
        return

    # Fetch ODK data
    logging.info("Starting data fetch from ODK API.")
    response = requests.get(ODK_API_URL, auth=ODK_AUTH)
    if response.status_code == 200:
        logging.info("Successfully fetched data from ODK.")
        odk_data = response.json().get("value", [])
        for record in odk_data:
            orgunit_uid = get_dhis2_orgunit_uid_by_nin(record.get("find_hf", {}).get("srch_nin"), DHIS2_API_URL, DHIS2_AUTH)
            if orgunit_uid and not data_value_exists_in_dhis2(record.get("find_hf", {}).get("srch_nin"), orgunit_uid, DHIS2_API_URL, DHIS2_AUTH):
                data_values = map_odk_to_dhis2(record, calculate_element_mapping, non_calculate_element_mapping)
                tracker_payload = create_tracker_payload(record, orgunit_uid, data_values)
                if push_to_dhis2(tracker_payload, DHIS2_API_URL, session):
                    print("Data pushed successfully.")
    else:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}")

    session.close()

if __name__ == "__main__":
    main()
