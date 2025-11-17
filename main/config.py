import json

def load_config(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def save_config(file_path: str, config: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)
        
def check_config(required_keys: list) -> bool:
    return all(key in load_config('main/config.json') for key in required_keys)