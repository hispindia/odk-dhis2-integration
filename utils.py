import logging
from datetime import datetime

def configure_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

def assign_value_if_not_null(value):
    return value if value else None

def format_date(date_value):
    return datetime.fromisoformat(date_value).strftime('%Y-%m-%d') if date_value else None

def remove_null_values(data):
    return [item for item in data if item["value"] is not None]
