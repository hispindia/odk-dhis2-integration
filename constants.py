from datetime import datetime
import os
ODK_API_BASE_URL = "https://iphs.abdm.gov.in/v1/projects/1/forms/iphs_database.svc/Submissions"
def construct_odk_api_url(limit):
    limit_str = f"?$top={limit}"
    full_url = ODK_API_BASE_URL 
    return full_url


limit = 10  

ODK_API_URL = construct_odk_api_url(limit)

DHIS2_API_URL = "https://iphs.nipi-cure.org/api"
ODK_AUTH = os.getenv("ODK_AUTH")
DHIS2_AUTH = os.getenv("DHIS2_AUTH")
LOG_FILE = datetime.now().strftime("%Y-%m-%d") + "_integration_abdm.log"
