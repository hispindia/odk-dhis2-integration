import os

auth_file = "auth.enc"
if os.path.exists(auth_file):
    with open(auth_file) as f:
        auth_data = dict(line.strip().split('=', 1) for line in f if '=' in line)
else:
    raise FileNotFoundError("Authentication file not found!")

ODK_API_URL = "https://iphs.abdm.gov.in/v1/projects/1/forms/iphs_database.svc/Submissions?$filter=__system/submissionDate ge 2025-01-05&$skip=10&$top=1"
ODK_AUTH = (auth_data.get("ODK_USERNAME"), auth_data.get("ODK_PASSWORD"))

DHIS2_API_URL = "https://iphs.nipi-cure.org/api"
DHIS2_AUTH = (auth_data.get("DHIS2_USERNAME"), auth_data.get("DHIS2_PASSWORD"))

LOG_FILE = "hr_data_push.log"
PROGRAM_STAGE_ID = "hiF9ywHeAlE"
TRACKED_ENTITY_TYPE = "tbqOAw2BJIe"
PROGRAM_ID = "xHqM68DpuZj"
