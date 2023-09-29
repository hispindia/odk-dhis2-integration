# main.py
import requests
from datetime import datetime
from constants import ODK_AUTH, ODK_API_URL, DHIS2_API_URL, DHIS2_AUTH
from utils import (
    configure_logging,
    log_info,
    log_error,
    get_dhis2_orgunit_uid_by_block_district,
    data_value_exists_in_dhis2,
)

def fetch_odk_data():
    try:
        today_date = datetime.now().strftime("%Y-%m-%d")
        updated_odk_api_url = f"{ODK_API_URL}?$filter=__system/submissionDate ge {today_date}"

        response = requests.get(updated_odk_api_url, auth=ODK_AUTH)
        print("Data fetched for:", updated_odk_api_url)

        if response.status_code == 200:
            log_info("ODK data fetched successfully.")
            return response.json()["value"]
        else:
            log_error("Failed to fetch ODK data.")
            return []
    except Exception as e:
        log_error("An error occurred while fetching ODK data:", str(e))
        return []
    
def remove_null_values(obj):
    if isinstance(obj, dict):
        return {key: remove_null_values(value) for key, value in obj.items() if value is not None and value != "null"}
    elif isinstance(obj, list):
        return [remove_null_values(item) for item in obj if item is not None and item != "null"]
    else:
        return obj
    
def assign_value_if_not_null(value):
    if value is not None and value != "null":
        return value
    else:
        return None

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%y-%m-%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError:
        return None
    
def convert_to_boolean(value):
    if value == "1":
        return "true"
    elif value == "0":
        return "false"
    else:
        return None
    
def transform_to_dhis2_events(odk_data):
    tracker_payloads = []

    for submission in odk_data:
        block_name = submission["login_pin"]["Block"]
        district_name = submission["login_pin"]["District"]
        orgunit_uid = get_dhis2_orgunit_uid_by_block_district(block_name, district_name)
        print("--",orgunit_uid)
        print("name--",block_name,"--",district_name)
        if orgunit_uid:
            event_id = submission["g_info"]["patient_id"]
            if not data_value_exists_in_dhis2(event_id,orgunit_uid):
                tracker = {
                    "trackedEntityType": "",
                    "orgUnit": orgunit_uid,
                    "attributes": remove_null_values([
                        {"attribute": "taR4U6rFoJe", "value": assign_value_if_not_null(submission["login_pin"]["mobile"])}
                    ]),
                    "enrollments": [
                        {
                            "orgUnit": orgunit_uid,
                            "program": "",
                            "enrollmentDate": submission["g_info"]["cdate"],
                            "incidentDate": submission["g_info"]["cdate"],
                            "dueDate": submission["g_info"]["cdate"],
                            "events": [
                                {
                                    "program": "eXm5MqSJmkc",
                                    "orgUnit": orgunit_uid,
                                    "eventDate": submission["g_info"]["cdate"],
                                    "status": "COMPLETED",
                                    "storedBy": "",
                                    "programStage": "eAWsPnKNnxr",
                                    "geometry":{"type":"Point","coordinates":[submission["login_pin"]["location"]["coordinates"][0],submission["login_pin"]["location"]["coordinates"][1]]},
                                    "dataValues": remove_null_values([           
                         {"dataElement": "jjrFSLhONiM", "value": assign_value_if_not_null(submission["age_group"]["ageindays"])}])}]}]}
                #declare from local file
               
                print("---",tracker)
                tracker_payloads.append(tracker)
                
            else:
                print("Event with uuid:", event_id, "already exists in DHIS2. Skipping.")
                log_info(f"Event with ID {event_id} already exists in DHIS2. Skipping.")
        else:
            log_info(f"DHIS2 organization unit not found for block: {block_name} and parent: {district_name}. Skipping.")
    return tracker_payloads

def push_to_dhis2(dhis2_events):
    try:
        for event in dhis2_events:
            response = requests.post(f"{DHIS2_API_URL}/trackedEntityInstances", json=event, auth=DHIS2_AUTH)
            if response.status_code != 200:
                log_error("Failed to create event in DHIS2 for: " + str(response.content))
        log_info(f"Ev----status-- {response.status_code} ")
        log_info(f"Ev---- {response} ")
        log_info("Data successfully pushed to DHIS2.")
    except Exception as e:
        log_error("An error occurred while pushing data to DHIS2: " + str(e))

def main():
    try:
        configure_logging()
        odk_data = fetch_odk_data()
        dhis2_events = transform_to_dhis2_events(odk_data)
        push_to_dhis2(dhis2_events)
    except Exception as e:
        log_error("An error occurred in the main process: " + str(e))

if __name__ == "__main__":
    main()
