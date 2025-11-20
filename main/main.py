from main._template import LOGGER, TMPDIR, TMPFILE
LOGGER.info("Starting UnrealGitUI application.")

#==== IMPORTS ==== #
import customtkinter as ctk
from tkinter import simpledialog
from main.config import load_config, save_config, check_config
from main.errors import ConfigError

#==== IMPORT UI TABS ==== #
from main.ui.tabs.terminal import TerminalUI
from main.ui.tabs.dashboard import DashboardUI

#==== CONFIGURATION ==== #
if not check_config(['app_title', 'git']):
    raise ConfigError("Missing required configuration keys.")

CONFIG = load_config('main/config.json')

#==== Global Functions ====#
def toggle_mode(event=None):
    if CONFIG.get("mode", "dark") == "dark":
        ctk.set_appearance_mode("light")
        CONFIG['mode'] = "light"
        save_config("main/config.json", CONFIG)
    elif CONFIG.get("mode", "dark") == "light":
        ctk.set_appearance_mode("dark")
        CONFIG['mode'] = "dark"
        save_config("main/config.json", CONFIG)
    else:
        ctk.set_appearance_mode("light")
        CONFIG['mode'] = "light"
        save_config("main/config.json", CONFIG)

#==== MAIN WINDOW ==== #
rootwin = ctk.CTk()
rootwin.title(CONFIG.get('app_title', 'ERROR LOADING TITLE'))
rootwin.geometry("800x930")
rootwin.resizable(False, False)
ctk.set_appearance_mode(CONFIG.get("mode", "dark"))

tabs = ctk.CTkTabview(rootwin)
tabs.pack(expand=True, fill='both', padx=20, pady=20)

dashboard_tab: ctk.CTkFrame = tabs.add("Dashboard")
workflow_tab: ctk.CTkFrame = tabs.add("Workflow") 
git_tools_tab: ctk.CTkFrame = tabs.add("Git Tools")
unreal_tools_tab: ctk.CTkFrame = tabs.add("Unreal Tools")
terminal_tab: ctk.CTkFrame = tabs.add("Terminal")
settings_tab: ctk.CTkFrame = tabs.add("Settings")

#==== ADD TABS CONTENT ==== #
dashboard_ui: DashboardUI = DashboardUI(dashboard_tab)
dashboard_ui.pack(expand=True, fill='both')

terminal_ui: TerminalUI = TerminalUI(terminal_tab)
terminal_ui.pack(expand=True, fill='both')

#==== Keybinds ====#
rootwin.bind_all("<Control-Shift-Alt-m>", lambda event: toggle_mode())

def run() -> None:
    rootwin.mainloop()