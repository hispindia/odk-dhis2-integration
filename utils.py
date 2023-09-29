# utils.py
import requests
import logging
from constants import DHIS2_API_URL, DHIS2_AUTH, LOG_FILE

def configure_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def get_dhis2_orgunit_uid_by_block_district(block, district):
    params = {
        "filter": f"displayName:like:{block}",
        "fields": "id,name,parent[id,name]",
    }
    response = requests.get(f"{DHIS2_API_URL}/organisationUnits", params=params, auth=DHIS2_AUTH)
    if response.status_code == 200:
        orgunits = response.json()["organisationUnits"]
        for orgunit in orgunits:
            parent_name = orgunit["parent"]["name"]
            if parent_name.lower() == district.lower():
                return orgunit["id"]
    return None

def data_value_exists_in_dhis2(event_id,orgunit_uid):
    try:
        response = requests.get(f"{DHIS2_API_URL}/trackedEntityInstances?ou={orgunit_uid}&program=eXm5MqSJmkc", params={"filter": f"vJ5V1IQXZjP:EQ:{event_id}"}, auth=DHIS2_AUTH)
        print("matching uuid--",response.url)
        if response.status_code == 200:
            events = response.json()["trackedEntityInstances"]
            print("length events--",len(events))
            return len(events) > 0
        return False
    except Exception as e:
        log_error("An error occurred while checking data value in DHIS2.", e)
        return False