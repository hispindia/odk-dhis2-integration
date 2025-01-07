def map_odk_to_dhis2(odk_data, calculate_element_mapping, non_calculate_element_mapping):
    data_values = []

    # Process calculate elements
    for key, value in odk_data.items():
        if key in calculate_element_mapping and value is not None:
            data_values.append({
                "dataElement": calculate_element_mapping[key],
                "value": value
            })

    # Process non-calculate elements
    for key, value in odk_data.items():
        if key in non_calculate_element_mapping and value is not None:
            values = str(value).split()
            for v in values:
                full_code = f"{key}_{v}"
                if full_code in non_calculate_element_mapping:
                    data_values.append({
                        "dataElement": non_calculate_element_mapping[full_code],
                        "value": v
                    })

    return data_values
