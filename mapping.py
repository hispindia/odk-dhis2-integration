def map_odk_to_dhis2(odk_data, data_element_mapping):
    data_values = []

    for key, value in odk_data.items():
        if key in data_element_mapping and value is not None:
            element_details = data_element_mapping[key]
            data_values.append({
                "dataElement": element_details["id"],
                "value": value
            })

    return data_values