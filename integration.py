import requests
from utils import remove_null_values, assign_value_if_not_null
import logging
def get_dhis2_orgunit_uid_by_nin(facility_nin, dhis2_url, dhis2_auth):
    params = {'fields': 'id,name,code', 'level': 5, 'filter': f'code:eq:{facility_nin}'}
    response = requests.get(f"{dhis2_url}/organisationUnits", params=params, auth=dhis2_auth)
    if response.status_code == 200:
        orgunits = response.json().get('organisationUnits', [])
        if orgunits:
            return orgunits[0]['id']
    return None

def data_value_exists_in_dhis2(event_id, orgunit_uid, dhis2_url, dhis2_auth):
    params = {"filter": f"VTCQOcgxnbu:EQ:{event_id}", "ou": orgunit_uid, "program": "bV4VOVumELH"}
    response = requests.get(f"{dhis2_url}/trackedEntityInstances", params=params, auth=dhis2_auth)
    if response.status_code == 200:
        events = response.json().get("trackedEntityInstances", [])
        return len(events) > 0
    return False

def fetch_data_element_mapping(dhis2_url, program_stage_id, dhis2_auth):
    url = f"{dhis2_url}/programStages/{program_stage_id}?fields=programStageDataElements[dataElement[id,name,code]]"
    response = requests.get(url, auth=dhis2_auth)
    if response.status_code == 200:
        program_stage_data = response.json()
        
        calculate_mapping = {
            element['dataElement']['name']: element['dataElement']['id']
            for element in program_stage_data['programStageDataElements']
            if 'calculate' in element['dataElement']['code']
        }
        non_calculate_mapping = {
            element['dataElement']['name'].replace('_raw_de_gov', ''): {
                "id": element['dataElement']['id'],
                "name": element['dataElement']['name']
            }
            for element in program_stage_data['programStageDataElements']
            if 'calculate' not in element['dataElement']['code']
        }
        return calculate_mapping, non_calculate_mapping
    else:
        raise Exception(f"Failed to fetch data element mappings. Status code: {response.status_code}")

def create_tracker_payload(submission, orgunit_uid, data_values):
    return {
        "trackedEntityType": "tbqOAw2BJIe",
        "orgUnit": orgunit_uid,
        "attributes": remove_null_values([
            {"attribute": "VTCQOcgxnbu", "value": assign_value_if_not_null(submission["find_hf"]["srch_nin"])},
            {"attribute": "FuCoXAHtiTN", "value": assign_value_if_not_null(submission["gen_info"]["FT"])},
            {"attribute": "MvZuYsmwW1k", "value": assign_value_if_not_null(submission["gen_info"]["FST"])}
        ]),
        "enrollments": [
            {
                "orgUnit": orgunit_uid,
                "program": "bV4VOVumELH",
                "enrollmentDate": submission["Assess_team"]["Date_of_Assessment"],
                "incidentDate": submission["Assess_team"]["Date_of_Assessment"],
                "dueDate": submission["Assess_team"]["Date_of_Assessment"],
                "events": [
                    {
                        "program": "bV4VOVumELH",
                        "orgUnit": orgunit_uid,
                        "eventDate": submission["Assess_team"]["Date_of_Assessment"],
                        "status": "COMPLETED",
                        "storedBy": "admin_import",
                        "programStage": "ZJ6HL7aOf8X",
                        "dataValues": data_values
                    }
                ]
            }
        ]
    }

def push_to_dhis2(payload, dhis2_url, session):
    headers = {'Content-Type': 'application/json'}
    response = session.post(f"{dhis2_url}/trackedEntityInstances", json=payload, headers=headers)
    if response.status_code == 200:
        logging.info(f"Successfully pushed data to DHIS2. Response: {response.json()}")
        return True
    else:
        logging.error(f"Failed to push data to DHIS2. Status Code: {response.status_code}, Response: {response.text}")
        return False
