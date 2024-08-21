def remove_None_values_from_dict(input_dict):
    return {k: v for k, v in input_dict.items() if v is not None}