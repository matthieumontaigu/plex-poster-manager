import json


def load_json_file(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
        return data


def save_json_file(file_path: str, data: dict) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
