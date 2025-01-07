def map_odk_to_dhis2(odk_data, calculate_element_mapping, non_calculate_element_mapping):
    data_values = []

    for key, value in odk_data.items():
        if key in calculate_element_mapping and value is not None:
            data_values.append({
                "dataElement": calculate_element_mapping[key],
                "value": value
            })

    for key, value in odk_data.items():
        if key in non_calculate_element_mapping and value is not None:
            element_details = non_calculate_element_mapping[key]
            data_values.append({
                "dataElement": element_details["id"],
                "value": value
            })

    return data_values
