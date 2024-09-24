import json


def save_to_jsonl(data, filename):
    """
    Save a list of dictionaries to a JSONL file.

    :param data: List of dictionaries to save
    :param filename: Name of the file to save to
    """
    with open(filename, "w") as f:
        for item in data:
            json_line = json.dumps(item)
            f.write(json_line + "\n")
