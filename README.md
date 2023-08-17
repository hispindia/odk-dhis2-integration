# odk-dhis2-integration
Automated data integration script to fetch survey submissions from Open Data Kit (ODK) and push them as events to the District Health Information System 2 (DHIS2). This script facilitates seamless synchronization of field data collected via ODK with DHIS2 for efficient health data management and reporting.

# ODK to DHIS2 Data Integration

This repository contains scripts to fetch data from the ODK Submissions API and push it to DHIS2 as events. The integration process involves transforming the data from ODK format to DHIS2 event format and handling existing event checks.

## Prerequisites

- Python 3.x
- pip package manager

## Installation

1. Clone this repository to your local machine.

   ```bash
   git clone https://github.com/hispindia/odk-dhis2-integration.git

2.  Navigate to project directory 

    cd odk-to-dhis2

3. Install the required Python packages using pip.

    pip install -r requirements.txt



## Configuration
    python .py

## Troubleshooting

If you encounter any issues or errors, please check the log files for more information. Log files are generated in the project directory with date-wise filenames.

