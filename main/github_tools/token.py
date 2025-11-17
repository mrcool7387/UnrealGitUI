from main.config import load_config, save_config
from tkinter import simpledialog
from main._template import LOGGER

CONFIG = load_config('main/config.json')

GIT_AUTH_TOKEN = CONFIG.get('git', {}).get('token', None)
if GIT_AUTH_TOKEN is None or GIT_AUTH_TOKEN == "":
    LOGGER.warning("Git authentication token is missing in configuration.")
    while True:
        GIT_AUTH_TOKEN = simpledialog.askstring("Git Authentication Token", "Please enter your Git authentication token:")
        if GIT_AUTH_TOKEN:
            CONFIG['git']['token'] = GIT_AUTH_TOKEN
            save_config('main/config.json', CONFIG)
            CONFIG = load_config('main/config.json')
            LOGGER.info("Git authentication token saved to configuration.")
            break