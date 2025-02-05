import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import winreg
import ctypes
import json
import requests
from datetime import datetime

class EmulatorSetup(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Android Emulator Setup")
        self.geometry("600x400")
        self.configure(bg='#f0f0f0')
        
        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"600x400+{x}+{y}")

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background='#f0f0f0')
        self.style.configure("Custom.TLabel", background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure("Header.TLabel", background='#f0f0f0', font=('Segoe UI', 12, 'bold'))
        
        self.create_widgets()
        self.setup_paths()

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self, style="Custom.TFrame", padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = ttk.Label(
            self.main_frame,
            text="Android Emulator Setup and Launcher",
            style="Header.TLabel"
        )
        self.header.pack(pady=(0, 20))

        # Progress frame
        self.progress_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
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
            style="Custom.TLabel"
        )
        self.status_label.pack()

        # Details text
        self.details_text = tk.Text(
            self.main_frame,
            height=10,
            width=60,
            font=('Consolas', 9),
            bg='#ffffff',
            wrap=tk.WORD
        )
        self.details_text.pack(pady=10)

        # Buttons frame
        self.button_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
        self.button_frame.pack(pady=10)

        # Start button
        self.start_button = ttk.Button(
            self.button_frame,
            text="Start Setup",
            command=self.start_setup
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Launch button (initially disabled)
        self.launch_button = ttk.Button(
            self.button_frame,
            text="Launch Emulator",
            command=self.launch_emulator,
            state=tk.DISABLED
        )
        self.launch_button.pack(side=tk.LEFT, padx=5)

    def setup_paths(self):
        self.ANDROID_HOME = os.path.join(os.path.expanduser("~"), "Desktop", "android tools")
        self.ANDROID_SDK_ROOT = self.ANDROID_HOME
        self.JAVA_HOME = r"C:\Program Files\Java\jdk-23"
        
    def update_status(self, message, progress=None):
        self.status_label.config(text=message)
        if progress is not None:
            self.progress['value'] = progress
        self.details_text.insert(tk.END, f"{message}\n")
        self.details_text.see(tk.END)
        self.update()

    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def check_windows_features(self):
        features = [
            "Microsoft-Windows-Subsystem-Linux",
            "VirtualMachinePlatform",
            "HypervisorPlatform"
        ]
        
        for feature in features:
            result = subprocess.run(
                f'dism /online /get-featureinfo /featurename:{feature}',
                capture_output=True,
                text=True
            )
            if "State : Enabled" not in result.stdout:
                return False
        return True

    def check_java(self):
        try:
            result = subprocess.run(
                [os.path.join(self.JAVA_HOME, "bin", "java"), "-version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def check_android_tools(self):
        required_files = [
            os.path.join(self.ANDROID_HOME, "cmdline-tools", "latest", "bin", "sdkmanager.bat"),
            os.path.join(self.ANDROID_HOME, "platform-tools", "adb.exe"),
            os.path.join(self.ANDROID_HOME, "emulator", "emulator.exe")
        ]
        
        return all(os.path.exists(f) for f in required_files)

    def run_command(self, command, silent=False):
        try:
            if silent:
                result = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )
            return result
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            return None

    def start_setup(self):
        if not self.check_admin():
            messagebox.showerror(
                "Admin Rights Required",
                "Please run this program as administrator!"
            )
            return

        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.setup_process, daemon=True).start()

    def setup_process(self):
        try:
            # Check Java
            self.update_status("Checking Java installation...", 10)
            if not self.check_java():
                self.update_status("Installing/Updating Java...")
                # Add Java installation logic here
                
            # Check Windows features
            self.update_status("Checking Windows features...", 20)
            if not self.check_windows_features():
                self.update_status("Enabling required Windows features...")
                self.run_command("dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart")
                self.run_command("dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart")
                self.run_command("dism /online /enable-feature /featurename:HypervisorPlatform /all /norestart")

            # Setup Android tools
            self.update_status("Setting up Android tools...", 40)
            if not self.check_android_tools():
                self.setup_android_tools()

            # Update components
            self.update_status("Updating Android components...", 60)
            self.update_android_components()

            # Create/update emulator
            self.update_status("Setting up emulator...", 80)
            self.setup_emulator()

            self.update_status("Setup complete!", 100)
            self.launch_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.update_status(f"Error during setup: {str(e)}")
            messagebox.showerror("Setup Error", str(e))
        finally:
            self.start_button.config(state=tk.NORMAL)

    def setup_android_tools(self):
        # Add detailed Android tools setup logic
        pass

    def update_android_components(self):
        os.environ["ANDROID_HOME"] = self.ANDROID_HOME
        os.environ["ANDROID_SDK_ROOT"] = self.ANDROID_SDK_ROOT
        os.environ["JAVA_HOME"] = self.JAVA_HOME
        
        # Update SDK components
        self.run_command(
            f'"{os.path.join(self.ANDROID_HOME, "cmdline-tools", "latest", "bin", "sdkmanager.bat")}" '
            '"platform-tools" "platforms;android-34" "system-images;android-34;google_apis;x86_64" "emulator"'
        )

    def setup_emulator(self):
        # Create AVD
        self.run_command(
            f'"{os.path.join(self.ANDROID_HOME, "cmdline-tools", "latest", "bin", "avdmanager.bat")}" '
            'create avd -n Pixel9Pro -k "system-images;android-34;google_apis;x86_64" -d pixel --force'
        )

    def launch_emulator(self):
        # Hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # Launch emulator in background
        threading.Thread(
            target=self.run_emulator,
            args=(startupinfo,),
            daemon=True
        ).start()

    def run_emulator(self, startupinfo):
        emulator_path = os.path.join(self.ANDROID_HOME, "emulator", "emulator.exe")
        gpu_modes = ["host", "swiftshader_indirect", "angle_indirect", "guest"]
        
        for mode in gpu_modes:
            try:
                subprocess.Popen(
                    [emulator_path, "-avd", "Pixel9Pro", "-gpu", mode],
                    startupinfo=startupinfo
                )
                break
            except Exception:
                continue

if __name__ == "__main__":
    app = EmulatorSetup()
    app.mainloop()