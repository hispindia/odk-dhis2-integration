import requests
from constants import ODK_API_URL, ODK_AUTH, DHIS2_API_URL, DHIS2_AUTH, LOG_FILE, PROGRAM_STAGE_ID
from utils import configure_logging
from mapping import map_odk_to_dhis2
from integration import get_dhis2_orgunit_uid_by_nin, data_value_exists_in_dhis2, create_tracker_payload, push_to_dhis2, fetch_data_element_mapping
import logging


def main():

    configure_logging(LOG_FILE)
    session = requests.Session()
    session.auth = DHIS2_AUTH

    try:

        logging.info("Fetching data element mappings from DHIS2.")
        calculate_element_mapping, non_calculate_element_mapping = fetch_data_element_mapping(
            DHIS2_API_URL, PROGRAM_STAGE_ID, DHIS2_AUTH
        )
        logging.info(f"Fetched calculate element mapping: {calculate_element_mapping}")
        logging.info(f"Fetched non-calculate element mapping: {non_calculate_element_mapping}")

        logging.info("Starting data fetch from ODK API.")
        response = requests.get(ODK_API_URL, auth=ODK_AUTH)
        if response.status_code == 200:
            logging.info("Successfully fetched data from ODK.")
            odk_data = response.json().get("value", [])
            for record in odk_data:
                orgunit_uid = get_dhis2_orgunit_uid_by_nin(record.get("find_hf", {}).get("srch_nin"), DHIS2_API_URL, DHIS2_AUTH)
                if not orgunit_uid:
                    logging.warning(f"No org unit found for NIN: {record.get('find_hf', {}).get('srch_nin')}")
                    continue

                if data_value_exists_in_dhis2(record.get("find_hf", {}).get("srch_nin"), orgunit_uid, DHIS2_API_URL, DHIS2_AUTH):
                    logging.info(f"Data already exists for NIN: {record.get('find_hf', {}).get('srch_nin')}")
                    continue

                data_values = map_odk_to_dhis2(record, calculate_element_mapping, non_calculate_element_mapping)
                tracker_payload = create_tracker_payload(record, orgunit_uid, data_values)

                if push_to_dhis2(tracker_payload, DHIS2_API_URL, session):
                    logging.info(f"Data successfully pushed for NIN: {record.get('find_hf', {}).get('srch_nin')}")
                else:
                    logging.error(f"Failed to push data for NIN: {record.get('find_hf', {}).get('srch_nin')}")

        else:
            logging.error(f"Failed to fetch data from ODK. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"An error occurred during Services domain integration: {str(e)}")
    finally:
        session.close()
        logging.info("Session closed.")


if __name__ == "__main__":
    main()
