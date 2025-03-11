# constants.py

from datetime import datetime

ODK_API_URL = "https://odk.nipi-cure.org/v1/projects/9/forms/dss_child_health.svc/Submissions"
# ODK_API_URL = "https://odk.nipi-cure.org/v1/projects/9/forms/dss_health.svc/Submissions?$filter=__system/submissionDate ge 2024-02-01 and __system/submissionDate le 2024-02-0"
DHIS2_API_URL = "http://172.105.253.84:8665/odk_nipi/api"

ODK_AUTH = ("dss.nipi@hispindia.org", "*****")

DHIS2_AUTH = ("*****", "*****")
LOG_FILE = datetime.now().strftime("%Y-%m-%d") + "_integration.log"




