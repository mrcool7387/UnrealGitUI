import os
import threading
import time
import customtkinter as ctk
from CTkTable import CTkTable
from github.GitRelease import GitRelease
from main._template import LOGGER
from main.ctk_external_modules.CTkCollapsibleFrame import CTkCollapsiblePanel
from main.github_tools.dashboard import get_repo_info, get_last_commit, get_commits_since, get_prs, get_last_release, get_last_x_commits
from main.config import load_config

CONFIG = load_config('main/config.json')

class DashboardUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        LOGGER.info("Initializing Dashboard UI components.")

        # Obere Frames nebeneinander
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Status Frame created. {}".format(repr(self.status_frame)))
        self.commit_table_frame = ctk.CTkFrame(self)
        self.commit_table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Commit Table Frame created. {}".format(repr(self.commit_table_frame)))

        # Untere Frames nebeneinander
        self.commit_details_frame = ctk.CTkFrame(self)
        self.commit_details_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Commit Details Frame created. {}".format(repr(self.commit_details_frame)))
        self.start_frame = ctk.CTkFrame(self)
        self.start_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Start Frame created. {}".format(repr(self.start_frame)))

        # Collapsible Logs Frame
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Log Frame created. {}".format(repr(self.log_frame)))
        
        logs_collapsible: CTkCollapsiblePanel = CTkCollapsiblePanel(self.log_frame, title="Logs")
        logs_collapsible.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        LOGGER.debug("Logs Collapsible Panel created. {}".format(repr(logs_collapsible)))

        # Scrollbar + Textbox (schwarzer Hintergrund)
        self.log_textbox = ctk.CTkTextbox(
            logs_collapsible._content_frame, 
            width=700, 
            height=300,
            corner_radius=5,
            fg_color="#1e1e1e",  # dunkelgrau/schwarz
            text_color="white",
            state="disabled"
        )
        self.log_textbox.pack(side="left", fill="both", expand=True, padx=(0,0), pady=(0,0))

        # Scrollbar hinzufügen
        scrollbar = ctk.CTkScrollbar(logs_collapsible._content_frame, orientation="vertical", command=self.log_textbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_textbox.configure(yscrollcommand=scrollbar.set)

        # Grid-Konfiguration
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)  # Logs größer machen
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._stop_log_thread = False
        threading.Thread(target=self.update_logs_loop, daemon=True).start()
        LOGGER.info("Dashboard UI components initialized successfully.")
        
        
        self.load_data()
    
    def insert_log(self, message: str) -> None:
        self.log_textbox.after(0, self._insert_log_ui, message)

    def _insert_log_ui(self, message: str):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    
    def find_latest_log(self):
        files: list[str] = os.listdir("logs/")
        files: list[str] = [os.path.join("logs/", f) for f in files if f.endswith(".log")]
        if not files:
            return None
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]

    # ========== Log-Update-Loop ==========
    def update_logs_loop(self):
        last_size = 0
        latest_file = None
        while not self._stop_log_thread:
            try:
                file_path = self.find_latest_log()
                if file_path != latest_file:
                    latest_file = file_path
                    last_size = 0
                    self.log_textbox.delete("1.0", "end")
                if latest_file:
                    with open(latest_file, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        new_content = f.read()
                        if new_content:
                            self.insert_log(new_content)
                        last_size = f.tell()
            except Exception as e:
                LOGGER.error(f"Error reading log: {e}")
            time.sleep(1)


    def load_data(self):
        LOGGER.info("Loading dashboard data...")
        
        REPO = "{}/{}".format(CONFIG['git']['user'], CONFIG['git']['repo'])
        
        # Status Frame
        status_data: dict[str, str | int] = get_repo_info(REPO)
        status_data['commits'] = get_commits_since(REPO, since_datetime=None).totalCount
        status_data['prs'] = get_prs(REPO)
        last_release: None | GitRelease = get_last_release(REPO)
        status_data['last_release'] = str(last_release) if last_release else "N/A"
        LOGGER.debug("Status Data: {}".format(status_data))
        
        # ========== Status Table ==========
        status_data_values: list[list[str]] = []
        for key, value in status_data.items():
            status_data_values.append([key.replace("_", " ").capitalize(), str(value)])
        
        status_table = CTkTable(
            self.status_frame, 
            values=status_data_values, 
            row= len(status_data_values), 
            column=2,  # 2 Spalten: Name und Wert
            width=400
        )
        status_table.pack(fill="both", padx=5, pady=5, expand=True)
        
        # ========== Last 5 Commits Table ==========
        last_five_commits = get_last_x_commits(REPO, CONFIG.get("dashboard", {}).get("last_commits", 5))
        table_data: list[list[str]] = [["SHA", "Add", "Del", "Total"]]
        for c in last_five_commits:
            table_data.append([str(c.sha[:10]) + "...", str(c.stats.additions), str(c.stats.deletions), str(c.stats.total)])
        
        commit_table_label = ctk.CTkLabel(self.commit_table_frame, text=f"Last {len(last_five_commits)} Commits", font=("", 14))
        commit_table_label.pack(pady=10)
        
        commit_table = CTkTable(
            self.commit_table_frame, 
            values=table_data, 
            row=len(table_data), 
            column=len(table_data[0]), 
            width=300
        )
        commit_table.pack(fill="both", padx=5, pady=5, expand=True)
        
        # ========== Last Commit Details ==========
        last_commit = get_last_commit(REPO)
        if last_commit:
            details_data = [
                ["SHA", last_commit.sha],
                ["Kurze Nachricht", last_commit.commit.message.splitlines()[0]],
                ["Ausführliche Nachricht", last_commit.commit.message],
                ["Autor", last_commit.commit.author.name],
                ["Autor Email", last_commit.commit.author.email],
                ["Datum", str(last_commit.commit.author.date)],
                ["Dateien geändert", len([f.filename for f in last_commit.files])]
            ]
            commit_details_label = ctk.CTkLabel(self.commit_details_frame, text="Last Commit Details", font=("", 14))
            commit_details_label.pack(pady=10)
            
            details_table = CTkTable(
                self.commit_details_frame,
                values=details_data,
                row=len(details_data),
                column=2,
                width=600
            )
            details_table.pack(fill="both", padx=5, pady=5, expand=True)
        
        PATHS: dict = CONFIG.get('paths', {})
        unreal_check = os.path.exists(PATHS.get('unreal', None)) and str(PATHS.get('unreal', "")).endswith('.exe')  # type: ignore
        unreal_project_check = os.path.exists(PATHS.get('unreal_project_file', None)) and str(PATHS.get('unreal_project_file', "")).endswith('.uproject')  # type: ignore
        git_check = os.path.exists(PATHS.get('git', None)) and str(PATHS.get('git', "")).endswith('.exe') # type: ignore
        
        LOGGER.info(f"Unreal ({unreal_check}): {PATHS.get('unreal', None)}")
        LOGGER.info(f"Unreal Project File ({unreal_project_check}): {PATHS.get('unreal_project_file', None)}")
        LOGGER.info(f"Git ({git_check}): {PATHS.get('git', None)}")
        
        workflow_table = CTkTable(
            self.start_frame, 
            values=[
                ["Unreal", "Found" if unreal_check else "Not Found"], 
                ["Unreal Project File", "Found" if unreal_project_check else "Not Found"], 
                ["Git", "Found" if git_check else "Not Found"]
            ]
        )
        workflow_table.pack(fill="both", padx=5, pady=5, expand=True)
        
        self.start_button = ctk.CTkButton(self.start_frame, text="Start Workflow", command=lambda: LOGGER.info("Start Workflow button clicked"))
        self.start_button.pack(padx=20, pady=20)
        
        if unreal_check and unreal_project_check and git_check:
            self.start_button.configure(state="normal", fg_color="#187e18")  # aktiv & grün
        else:
            self.start_button.configure(state="disabled", fg_color="#8a0000")  # deaktiviert & rot

        
        LOGGER.info("Dashboard data loaded.")
