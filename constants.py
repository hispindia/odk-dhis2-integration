# constants.py

from datetime import datetime

# ODK_API_URL = "https://odk.nipi-cure.org/v1/projects/5/forms/Anaemia.svc/Submissions"
ODK_API_URL = "https://odk.nipi-cure.org/v1/projects/12/forms/dss_health.svc/Submissions"
DHIS2_API_URL = "http://172.105.253.84:8665/odk_nipi/api"

ODK_AUTH = ("sourabh.bhardwaj@hispindia.org", "")
DHIS2_AUTH = ("###", "###")

LOG_FILE = datetime.now().strftime("%Y-%m-%d") + "_integration.log"