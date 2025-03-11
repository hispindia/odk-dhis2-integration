# main.py
import requests
from datetime import datetime
from constants import ODK_AUTH,ODK_API_URL,DHIS2_API_URL,DHIS2_AUTH
from utils import configure_logging, log_info, log_error, get_dhis2_orgunit_uid_by_block_district,data_value_exists_in_dhis2,sendEmail

def fetch_odk_data():
    try:
        today_date = datetime.now().strftime("%Y-%m-%d")
        #updated_odk_api_url = f"{ODK_API_URL}?$filter=__system/submissionDate ge {today_date}"
        updated_odk_api_url = f"{ODK_API_URL}?$filter=__system/submissionDate ge 2024-10-09"
        print("data fetching for: ",updated_odk_api_url)
        response = requests.get(updated_odk_api_url, auth=ODK_AUTH)
        
        if response.status_code == 200:
            log_info(f"ODK data fetched successfully.")
            print(f"ODK data fetched successfully.")
            return response.json()["value"]
        else:
            log_error("Failed to fetch ODK data.")
            return []
    except Exception as e:
        log_error("An error occurred while fetching ODK data--", e)
        return []

def transform_to_dhis2_events(odk_data):
    dhis2_events = []

    for index, submission in enumerate(odk_data):
        block_name = submission["location_camp"]["block"]
        district_name = submission["location_camp"]["district"]
        orgunit_uid = get_dhis2_orgunit_uid_by_block_district(block_name, district_name)
        if orgunit_uid:
            # uuid:6f9d9577-90f6-4668-ae33-4bd0cadc7011
            event_id = submission["__id"].split(":")[1]
            if not data_value_exists_in_dhis2(event_id):
                print(f"for row { index +1}, Event with ID  {event_id} not exists in DHIS2. Adding. for orgunit_uid {orgunit_uid}, for date {submission["location_camp"]["date_camp"]}")
                log_info(f"for row { index +1}, Event with ID {event_id} not exists in DHIS2. Adding. for orgunit_uid {orgunit_uid}, for date {submission["location_camp"]["date_camp"]}")
                # log_info("event---")
                event = {
                "eventDate": submission["location_camp"]["date_camp"],
                "orgUnit": orgunit_uid,
                "program": "OSZGBa7ap1d",
                "dataValues": [
                    {"dataElement": "PuO8ZfalloM", "value": submission["location_camp"]["tested_at"]},
                    {"dataElement": "g5lnjsR2mi4", "value": submission["location_camp"]["camp_location"]},
                    {"dataElement": "QnK3KeJVLzN", "value": submission["location_camp"]["address"]},
                    {"dataElement": "qPPuaPj3wy9", "value": submission["Child_adult"]["name_p"]},
                    {"dataElement": "q2FWKpMyRSA", "value": submission["Child_adult"]["gender"]},
                    {"dataElement": "GoTBOz1huaK", "value": submission["Child_adult"]["preorlac"]},
                    {"dataElement": "kPSiW4ngmWO", "value": submission["Child_adult"]["result"]},
                    {"dataElement": "fTsT5tCMQR4", "value": submission["Child_adult"]["classify_all"]},
                    {"dataElement": "ZSsWwLEqGKk", "value": submission["Child_adult"]["weight_kg"]},
                    {"dataElement": "jWTOfbCiGMV", "value": submission["Child_adult"]["agegrp_text"]},
                    {"dataElement": "Bjh3nyIKHi3", "value": submission["Child_adult"]["preglact_text"]},
                    {"dataElement": "zkhndIoBYH7", "value": submission["__id"]}
                ],
            }
                dhis2_events.append(event)
            else:
                print(f"for row { index +1},Event with uuid:, {event_id} , for date {submission["location_camp"]["date_camp"]} already exists in DHIS2. Skipping.")
                log_info(f"for row { index +1}, Event with ID {event_id}, , for date {submission["location_camp"]["date_camp"]} already exists in DHIS2. Skipping.")
        else:
            log_info(f"DHIS2 organization unit not found for block: {block_name} and parent: {district_name}. Skipping.")
            print("DHIS2 organization unit not found for block:", block_name, "and parent:", district_name, "Skipping.")
    return dhis2_events

def push_to_dhis2(dhis2_events):
    try:
        for event in dhis2_events:
            response = requests.post(f"{DHIS2_API_URL}/events", json=event, auth=DHIS2_AUTH)
            # print("response--", response)
            if response.status_code != 200:
                log_error("Failed to create event in DHIS2 for: " + str(response.content))

        log_info("Events successfully pushed to DHIS2.")

    except Exception as e:
        log_error("An error occurred while pushing data to DHIS2: " + str(e))



def main():
    try:
        configure_logging()
        current_time_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print( f"pushing Anemia event Program data into DHIS2 start . { current_time_end }" )
        log_info(f"pushing Anemia event Program data into DHIS2 start . { current_time_end }")
        odk_data = fetch_odk_data()
        dhis2_events = transform_to_dhis2_events(odk_data)
        if dhis2_events:
            push_to_dhis2(dhis2_events)
    except Exception as e:
        log_error("An error occurred in the main process: " + str(e))

if __name__ == "__main__":
    main()

    current_time_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print( f"pushing Anemia event Program data into DHIS2 finished . { current_time_end }" )
    log_info(f"pushing Anemia event Program data into DHIS2 finished . { current_time_end }")
    sendEmail()
