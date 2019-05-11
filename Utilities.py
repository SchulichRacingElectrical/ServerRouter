import json

def createJSON(data):
    json_str = json.dumps(data)
    return json_str


def readify_data(data):
    return createJSON(data).encode("UTF-8")

def string_me(data):
    return json.loads(data.decode('utf-8'))

def replace_value_with_definition(current_dict, key_to_find, definition):
    for key in current_dict.keys():
        if key == key_to_find:
            current_dict[key] = definition
    return current_dict