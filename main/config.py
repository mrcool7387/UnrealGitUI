import json
import os
from dotenv import load_dotenv
from main.errors import MissingDotEnvFile, MissingGithubToken
from main._template import LOGGER

def load_config(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        config = json.load(file)
    if os.path.exists('main/.env'):
        load_dotenv('main/.env')
        token: str | None = os.getenv('GITHUB_TOKEN')
        if not token:
            raise MissingGithubToken('Your Github Token is Missing in the `main/.env` file, or there is no Entry named `GITHUB_TOKEN` in the `main/.env` file')
        config['git']['token'] = token
    else:
        raise MissingDotEnvFile('Your .env file at `main/.env` is missing')
    
    LOGGER.info(f'Config loaded: {config}')
    return config

def save_config(file_path: str, config: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)
        
def check_config(required_keys: list) -> bool:
    return all(key in load_config('main/config.json') for key in required_keys)