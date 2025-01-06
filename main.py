import requests
from datetime import datetime
from constants import ODK_AUTH, ODK_API_URL, DHIS2_API_URL, DHIS2_AUTH
from utils import (
    configure_logging,
    log_info,
    log_error,
    get_dhis2_orgunit_uid_by_nin,
    data_value_exists_in_dhis2,
)

def fetch_odk_data():
    try:
        today_date = datetime.today().strftime('%Y-%m-%d')

        params = {
           "$select": (
                "find_hf/BLOCK_NAME,"
                "find_hf/DISTRICT_NAME,"
                "find_hf/Facility,"
                "find_hf/srch_nin,"
                "gen_info/FT,"
                "gen_info/FST,"
                "Assess_team/Date_of_Assessment,"
                "FINAL_MARKS_PER_DIAGNOSTIC,"
                "FINAL_MARKS_PER_DRUGS,"
                "FINAL_MARKS_PER_GOVERNANCE,"
                "FINAL_MARKS_PER_HR,"
                "FINAL_MARKS_PER_INFRASTRUCTURE,"
                "FINAL_MARKS_PER_SERVICES,"
                "FINAL_MARKS_WEIGHTED_RESULT"
            ),
            "$filter": f"__system/submissionDate ge {today_date}"
        }

        complete_url = f"{ODK_API_URL}?$filter=__system/submissionDate ge {today_date}"
        
        response = requests.get(ODK_API_URL, auth=ODK_AUTH, params=params)
        
        print(f"Data fetched for: {complete_url}")

        if response.status_code == 200:
            if response.json() and "value" in response.json():
                log_info("ODK data fetched successfully.")
                return response.json()["value"]
            else:
                log_error("Invalid or missing JSON content in the ODK response.")
                return []
        else:
            log_error(f"Failed to fetch ODK data. Status code: {response.status_code}")
            return []
    except Exception as e:
        log_error(f"An error occurred while fetching ODK data: {e}")
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

def transform_and_push_to_dhis2(submission):
    block_name = submission["find_hf"]["BLOCK_NAME"]
    district_name = submission["find_hf"]["DISTRICT_NAME"]
    facility_name = submission["find_hf"]["Facility"]
    facility_nin = submission["find_hf"]["srch_nin"]
    orgunit_uid = get_dhis2_orgunit_uid_by_nin(facility_nin)
    print(facility_nin)
    if orgunit_uid:
        event_id = str(submission["find_hf"]["srch_nin"])
        if not data_value_exists_in_dhis2(event_id, orgunit_uid):
            tracker = {
                "trackedEntityType": "tbqOAw2BJIe",
                "orgUnit": orgunit_uid,
                "attributes": remove_null_values([
                    {"attribute": "VTCQOcgxnbu", "value": assign_value_if_not_null(submission["find_hf"]["srch_nin"])},
                    {"attribute": "FuCoXAHtiTN", "value": str(submission["gen_info"]["FT"])},
                    {"attribute": "MvZuYsmwW1k", "value": assign_value_if_not_null(submission["gen_info"]["FST"])},
                ]),
                "enrollments": [
                    {
                        "orgUnit": orgunit_uid,
                        "program": "Hn9YUipbpZO",
                        "enrollmentDate": submission["Assess_team"]["Date_of_Assessment"],
                        "incidentDate": submission["Assess_team"]["Date_of_Assessment"],
                        "dueDate": submission["Assess_team"]["Date_of_Assessment"],
                        "events": [
                            {
                                "program": "Hn9YUipbpZO",
                                "orgUnit": orgunit_uid,
                                "eventDate": submission["Assess_team"]["Date_of_Assessment"],
                                "status": "COMPLETED",
                                "storedBy": "dhis2_user",
                                "programStage": "XObObOyKgio",
                                "dataValues": remove_null_values([
                                    {"dataElement": "RCweSlurQ40", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_DIAGNOSTIC"])},
                                    {"dataElement": "amoGQXXTFiQ", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_DRUGS"])},
                                    {"dataElement": "TgiuaZPTGCq", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_GOVERNANCE"])},
                                    {"dataElement": "FIGT2e7Wd1K", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_HR"])},
                                    {"dataElement": "wgU5bckubnl", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_INFRASTRUCTURE"])},
                                    {"dataElement": "YWzO8JzjrqC", "value": assign_value_if_not_null(submission["FINAL_MARKS_PER_SERVICES"])},
                                    {"dataElement": "SeocJdHrMHJ", "value": assign_value_if_not_null(submission["FINAL_MARKS_WEIGHTED_RESULT"])}
                                ])
                            }
                        ]
                    }
                ]
            }
            print("--event date--", submission["Assess_team"]["Date_of_Assessment"])
            push_to_dhis2(tracker)
        else:
            log_info(f"Event with ID {event_id} already exists in DHIS2. Skipping.")
    else:
        log_info(f"DHIS2 organization unit not found for facility nin: {facility_nin} -- block: {block_name} and parent: {district_name}. Skipping.")

def push_to_dhis2(event):
    try:
        print(f"Pushing event data to DHIS2 for orgUnit: {event['orgUnit']}")
        response = requests.post(f"{DHIS2_API_URL}/trackedEntityInstances", json=event, auth=DHIS2_AUTH)
        if response.status_code != 200:
            try:
                response_content = response.json()
            except ValueError:
                response_content = response.content.decode('utf-8')
            log_error(f"Failed to create event in DHIS2. Status code: {response.status_code}, Response: {response_content}")
            if isinstance(response_content, dict) and 'conflicts' in response_content:
                for conflict in response_content['conflicts']:
                    log_error(f"DHIS2 Conflict: {conflict['object']} - {conflict['value']}")
        else:
            log_info(f"Event created successfully in DHIS2. Response: {response.content.decode('utf-8')}")
    except Exception as e:
        log_error(f"An error occurred while pushing data to DHIS2: {e}")

def main():
    try:
        configure_logging()
        print("Starting ODK data fetch process...")
        odk_data = fetch_odk_data()
        print(f"Fetched {len(odk_data)} submissions from ODK.")
        
        print("Transforming and pushing ODK data to DHIS2 events...")
        request_count = 0
        for submission in odk_data:
            transform_and_push_to_dhis2(submission)
            request_count += 1
            print(f"Number of requests made so far: {request_count}")
        
        print("Process completed successfully.")
    except Exception as e:
        log_error(f"An error occurred in the main process: {e}")

if __name__ == "__main__":
    main()
