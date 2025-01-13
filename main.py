import requests
from constants import ODK_API_URL, ODK_AUTH, DHIS2_API_URL, DHIS2_AUTH, LOG_FILE, PROGRAM_STAGE_ID
from utils import configure_logging
from mapping import map_odk_to_dhis2
from integration import get_dhis2_orgunit_uid_by_nin, data_value_exists_in_dhis2, create_tracker_payload, push_to_dhis2, fetch_data_element_mapping
import logging


def fetch_odk_data_in_batches(api_url, auth, batch_size=1000):
    offset = 0
    all_data = []

    while True:
        params = {
            "limit": batch_size,
            "offset": offset
        }
        response = requests.get(api_url, auth=auth, params=params)

        if response.status_code == 200:
            batch_data = response.json().get("value", [])
            if not batch_data:
                break 
            all_data.extend(batch_data)
            offset += batch_size
        else:
            logging.error(f"Failed to fetch data from ODK. Status code: {response.status_code}, Response: {response.text}")
            break

    return all_data


def main():

    configure_logging(LOG_FILE)
    session = requests.Session()
    session.auth = DHIS2_AUTH

    try:
        logging.info("Fetching data element mappings from DHIS2.")
        data_element_mapping = fetch_data_element_mapping(DHIS2_API_URL, PROGRAM_STAGE_ID, DHIS2_AUTH)
        logging.info(f"Fetched data element mapping: {data_element_mapping}")

        logging.info("Starting data fetch from ODK API in batches.")
        odk_data = fetch_odk_data_in_batches(ODK_API_URL, ODK_AUTH)
        logging.info(f"Total records fetched: {len(odk_data)}")

        for record in odk_data:
            orgunit_uid = get_dhis2_orgunit_uid_by_nin(record.get("find_hf", {}).get("srch_nin"), DHIS2_API_URL, DHIS2_AUTH)
            if not orgunit_uid:
                logging.warning(f"No org unit found for NIN: {record.get('find_hf', {}).get('srch_nin')}")
                continue

            if data_value_exists_in_dhis2(record.get("find_hf", {}).get("srch_nin"), orgunit_uid, DHIS2_API_URL, DHIS2_AUTH):
                logging.info(f"Data already exists for NIN: {record.get('find_hf', {}).get('srch_nin')}")
                continue

            data_values = map_odk_to_dhis2(record, data_element_mapping)
            tracker_payload = create_tracker_payload(record, orgunit_uid, data_values)

            if push_to_dhis2(tracker_payload, DHIS2_API_URL, session):
                logging.info(f"Data successfully pushed for NIN: {record.get('find_hf', {}).get('srch_nin')}")
            else:
                logging.error(f"Failed to push data for NIN: {record.get('find_hf', {}).get('srch_nin')}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    finally:
        session.close()
        logging.info("Session closed.")

if __name__ == "__main__":
    main()
