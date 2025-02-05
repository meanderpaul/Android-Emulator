import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import zipfile
import io
import re
import pystray
from PIL import Image
import winreg
import logging
import tempfile
import time
from datetime import datetime

class EmulatorSetup(tk.Tk):
    VERSION = "1.0.3"
    GITHUB_REPO = "meanderpaul/Android-Emulator"
    COMPANY_NAME = "Android Emulator Setup"
    
    def __init__(self):
        # Add metadata at the start
        self.add_metadata()
        super().__init__()

        # Setup logging
        logging.basicConfig(
            filename='android_emulator.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Initialize paths and settings
        self.setup_paths()
        self.load_preferences()
        
        # Window setup
        self.title("Android Emulator")
        self.geometry("600x400")
        self.configure(bg='#f0f0f0')
        self.iconbitmap(os.path.join(self.ANDROID_HOME, "icon.ico"))
        
        # Center window
        self.center_window()
        
        # Initialize system tray
        self.setup_tray()
        
        # Create GUI
        self.create_widgets()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize emulator process tracking
        self.emulator_process = None
        self.monitor_thread = None

    def add_metadata(self):
        """Add metadata to help reduce false virus detections"""
        self.metadata = {
            'CompanyName': self.Paul,
            'FileDescription': 'Android Emulator Setup Tool',
            'FileVersion': self.1.0.3,
            'InternalName': 'android_setup',
            'LegalCopyright': f'© {datetime.now().year} {self.Paul}',
            'OriginalFilename': 'android_setup.exe',
            'ProductName': 'Android Emulator Setup',
            'ProductVersion': self.1.0.3
        }

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"600x400+{x}+{y}")

    def setup_paths(self):
        self.ANDROID_HOME = os.path.join(os.path.expanduser("~"), "Desktop", "android tools")
        self.ANDROID_SDK_ROOT = self.ANDROID_HOME
        self.JAVA_HOME = r"C:\Program Files\Java\jdk-23"
        self.preferences_file = os.path.join(self.ANDROID_HOME, "preferences.json")

    def load_preferences(self):
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
            else:
                self.preferences = {
                    'auto_start': False,
                    'minimize_to_tray': True,
                    'last_gpu_mode': 'host',
                    'cursor_integration': False
                }
                self.save_preferences()
        except Exception as e:
            logging.error(f"Error loading preferences: {e}")
            self.preferences = {}

    def save_preferences(self):
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving preferences: {e}")

    def setup_tray(self):
        try:
            image = Image.open(os.path.join(self.ANDROID_HOME, "icon.ico"))
            menu = (
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Launch Emulator", self.launch_emulator),
                pystray.MenuItem("Setup for Cursor", self.setup_for_cursor),
                pystray.MenuItem("Exit", self.quit_app)
            )
            self.tray_icon = pystray.Icon("android_emulator", image, "Android Emulator", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            logging.error(f"Error setting up tray icon: {e}")

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self, style="Custom.TFrame", padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))

        # Progress bar
        self.progress = ttk.Progressbar(
            self.progress_frame,
            length=500,
            mode='determinate'
        )
        self.progress.pack(pady=(0, 5))

        # Status label
        self.status_label = ttk.Label(
            self.progress_frame,
            text="Ready to start",
            wraplength=500
        )
        self.status_label.pack()

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.setup_button = ttk.Button(
            self.button_frame,
            text="Setup/Update",
            command=self.start_setup
        )
        self.setup_button.pack(side=tk.LEFT, padx=5)

        self.launch_button = ttk.Button(
            self.button_frame,
            text="Launch Emulator",
            command=self.launch_emulator,
            state=tk.DISABLED
        )
        self.launch_button.pack(side=tk.LEFT, padx=5)

        self.cursor_button = ttk.Button(
            self.button_frame,
            text="Setup for Cursor",
            command=self.setup_for_cursor
        )
        self.cursor_button.pack(side=tk.LEFT, padx=5)

        # Settings
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings")
        self.settings_frame.pack(fill=tk.X, pady=10)

        self.auto_start_var = tk.BooleanVar(value=self.preferences.get('auto_start', False))
        self.minimize_var = tk.BooleanVar(value=self.preferences.get('minimize_to_tray', True))
        self.cursor_var = tk.BooleanVar(value=self.preferences.get('cursor_integration', False))

        ttk.Checkbutton(
            self.settings_frame,
            text="Auto-start emulator after setup",
            variable=self.auto_start_var,
            command=self.save_preferences
        ).pack(anchor=tk.W, padx=5)

        ttk.Checkbutton(
            self.settings_frame,
            text="Minimize to tray",
            variable=self.minimize_var,
            command=self.save_preferences
        ).pack(anchor=tk.W, padx=5)

        ttk.Checkbutton(
            self.settings_frame,
            text="Enable Cursor integration",
            variable=self.cursor_var,
            command=self.save_preferences
        ).pack(anchor=tk.W, padx=5)

    def verify_adb_connection(self):
        try:
            adb_path = os.path.join(self.ANDROID_HOME, "platform-tools", "adb.exe")
            # Wait for device to be ready
            subprocess.run([adb_path, "wait-for-device"], timeout=60)
            
            # Get device status
            result = subprocess.run(
                [adb_path, "devices"], 
                capture_output=True, 
                text=True
            )
            
            if "emulator-5554" in result.stdout:
                self.update_status("ADB connected to emulator")
                return True
            return False
        except Exception as e:
            logging.error(f"ADB connection error: {e}")
            return False

    def enable_dev_settings(self):
        try:
            adb_path = os.path.join(self.ANDROID_HOME, "platform-tools", "adb.exe")
            # Enable developer options
            subprocess.run([
                adb_path, "shell", "settings", "put", 
                "global", "development_settings_enabled", "1"
            ])
            # Enable USB debugging
            subprocess.run([
                adb_path, "shell", "settings", "put", 
                "global", "adb_enabled", "1"
            ])
            self.update_status("Developer settings enabled")
        except Exception as e:
            logging.error(f"Error enabling dev settings: {e}")

    def setup_for_cursor(self):
        """Configure environment for Cursor development"""
        try:
            # Create Cursor config directory if it doesn't exist
            cursor_config = os.path.expanduser("~/.cursor/config")
            os.makedirs(cursor_config, exist_ok=True)
            
            # Create or update Android development settings
            android_settings = {
                "sdk": self.ANDROID_HOME,
                "adb": os.path.join(self.ANDROID_HOME, "platform-tools", "adb.exe"),
                "emulator": os.path.join(self.ANDROID_HOME, "emulator", "emulator.exe"),
                "default_avd": "Pixel9Pro"
            }
            
            with open(os.path.join(cursor_config, "android.json"), "w") as f:
                json.dump(android_settings, f, indent=2)
                
            self.update_status("Cursor Android development settings configured")
            self.preferences['cursor_integration'] = True
            self.save_preferences()
            
        except Exception as e:
            logging.error(f"Error setting up Cursor config: {e}")
            self.update_status(f"Error configuring Cursor: {str(e)}")

    def download_cmdline_tools(self):
        try:
            self.update_status("Downloading Android command-line tools...")
            
            response = requests.get("https://developer.android.com/studio")
            pattern = r'https://dl\.google\.com/android/repository/commandlinetools-win-[\d_]+\.zip'
            match = re.search(pattern, response.text)
            
            if not match:
                raise Exception("Could not find command-line tools download URL")
            
            download_url = match.group(0)
            response = requests.get(download_url, stream=True)
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                cmdline_tools_path = os.path.join(self.ANDROID_HOME, "cmdline-tools", "latest")
                os.makedirs(cmdline_tools_path, exist_ok=True)
                
                for file in zip_ref.namelist():
                    if file.startswith('cmdline-tools/'):
                        extract_path = os.path.join(cmdline_tools_path, *file.split('/')[1:])
                        if file.endswith('/'):
                            os.makedirs(extract_path, exist_ok=True)
                        else:
                            with zip_ref.open(file) as source, open(extract_path, 'wb') as target:
                                target.write(source.read())
            
            return True
        except Exception as e:
            logging.error(f"Error downloading command-line tools: {e}")
            return False

    def start_setup(self):
        self.setup_button.config(state=tk.DISABLED)
        threading.Thread(target=self.setup_process, daemon=True).start()

    def setup_process(self):
        try:
            # Download and extract command-line tools if needed
            if not os.path.exists(os.path.join(self.ANDROID_HOME, "cmdline-tools", "latest", "bin", "sdkmanager.bat")):
                if not self.download_cmdline_tools():
                    raise Exception("Failed to download Android command-line tools")

            # Set environment variables
            os.environ["ANDROID_HOME"] = self.ANDROID_HOME
            os.environ["ANDROID_SDK_ROOT"] = self.ANDROID_SDK_ROOT
            os.environ["JAVA_HOME"] = self.JAVA_HOME
            os.environ["PATH"] = f"{self.ANDROID_HOME}\\cmdline-tools\\latest\\bin;{os.environ['PATH']}"

            # Accept licenses
            self.update_status("Accepting Android SDK licenses...")
            subprocess.run("sdkmanager --licenses", input=b"y\n"*100, shell=True)

            # Install components
            self.update_status("Installing Android components...")
            subprocess.run('sdkmanager "platform-tools" "platforms;android-34" "system-images;android-34;google_apis;x86_64" "emulator"', shell=True)

            # Create AVD
            self.update_status("Creating Android Virtual Device...")
            subprocess.run('avdmanager create avd -n Pixel9Pro -k "system-images;android-34;google_apis;x86_64" -d pixel --force', shell=True)

            self.update_status("Setup complete!")
            self.launch_button.config(state=tk.NORMAL)

            if self.auto_start_var.get():
                self.launch_emulator()

        except Exception as e:
            logging.error(f"Setup error: {e}")
            self.update_status(f"Error: {str(e)}")
        finally:
            self.setup_button.config(state=tk.NORMAL)

    def launch_emulator(self):
        if self.emulator_process and self.emulator_process.poll() is None:
            messagebox.showinfo("Already Running", "Emulator is already running!")
            return

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            emulator_path = os.path.join(self.ANDROID_HOME, "emulator", "emulator.exe")
            self.emulator_process = subprocess.Popen(
                [emulator_path, "-avd", "Pixel9Pro", "-gpu", self.preferences.get('last_gpu_mode', 'host')],
                startupinfo=startupinfo
            )

            if self.minimize_var.get():
                self.withdraw()

            # Start ADB connection check
            def check_adb():
                time.sleep(10)  # Give emulator time to start
                if self.verify_adb_connection():
                    self.enable_dev_settings()
                    self.update_status("Emulator ready for development")
                else:
                    self.update_status("Warning: ADB connection not established")

            threading.Thread(target=check_adb, daemon=True).start()

            if not self.monitor_thread or not self.monitor_thread.is_alive():
                self.monitor_thread = threading.Thread(target=self.monitor_emulator, daemon=True)
                self.monitor_thread.start()

        except Exception as e:
            logging.error(f"Error launching emulator: {e}")
            messagebox.showerror("Error", f"Failed to launch emulator: {str(e)}")

    def monitor_emulator(self):
        while True:
            if self.emulator_process and self.emulator_process.poll() is not None:
                logging.info("Emulator process ended")
                self.emulator_process = None
                break
            threading.Event().wait(1.0)

    def update_status(self, message, progress=None):
        self.status_label.config(text=message)
        if progress is not None:
            self.progress['value'] = progress
        self.update()
        logging.info(message)

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def on_closing(self):
        if self.minimize_var.get():
            self.withdraw()
        else:
            self.quit_app()

    def quit_app(self):
        try:
            if self.emulator_process and self.emulator_process.poll() is None:
                self.emulator_process.terminate()
            self.tray_icon.stop()
            self.quit()
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
            self.quit()

if __name__ == "__main__":
    app = EmulatorSetup()
    app.mainloop()
