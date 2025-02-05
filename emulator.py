import subprocess
import os
import time
import sys

def setup_pixel9_emulator():
    """Sets up and launches a Google Pixel 9 Pro emulator"""
    
    # Check if required Android command-line tools are in PATH
    required_tools = ['avdmanager', 'sdkmanager', 'emulator', 'adb']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True)
        except FileNotFoundError:
            missing_tools.append(tool)
    
    if missing_tools:
        print("Error: Required Android tools not found in PATH:")
        print(f"Missing: {', '.join(missing_tools)}")
        print("\nTo fix this:")
        print("1. Download Android command-line tools from:")
        print("   https://developer.android.com/studio#command-tools")
        print("2. Extract them to a folder (e.g., C:\\Android\\cmdline-tools)")
        print("3. Add the following to your PATH:")
        print("   - C:\\Android\\cmdline-tools\\latest\\bin")
        print("   - C:\\Android\\emulator")
        print("   - C:\\Android\\platform-tools")
        return False

    # Install required system image if not present
    print("Checking/Installing system image (this may take a while)...")
    sys_image = "system-images;android-34;google_apis;x86_64"
    subprocess.run([
        'sdkmanager',
        '--install', sys_image,
        '--channel=0'
    ], capture_output=True)

    # Accept licenses
    subprocess.run(['sdkmanager', '--licenses'], input=b'y\n' * 100, capture_output=True)

    # Create Pixel 9 Pro AVD if it doesn't exist
    result = subprocess.run(['emulator', '-list-avds'], capture_output=True, text=True)
    if 'Pixel9Pro' not in result.stdout:
        print("Creating new Pixel 9 Pro AVD...")
        create_avd_cmd = [
            'avdmanager', 'create', 'avd',
            '--name', 'Pixel9Pro',
            '--package', sys_image,
            '--device', 'pixel'  # Using generic pixel device as pixel_9_pro might not be available
        ]

        try:
            subprocess.run(create_avd_cmd, input=b'no\n', check=True)  # 'no' to custom hardware profile
        except subprocess.CalledProcessError:
            print("Error creating AVD. Please check your Android SDK installation")
            return False

    # Launch emulator
    def launch_emulator():
        emulator_cmd = [
            'emulator',
            '-avd', 'Pixel9Pro',
            '-gpu', 'swiftshader_indirect',  # More compatible software rendering
            '-skin', '1440x3120',
            '-no-boot-anim',
            '-no-snapshot',
            '-no-audio',
            '-verbose'
        ]
        
        try:
            print("Starting emulator...")
            process = subprocess.Popen(emulator_cmd, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            
            # Wait to check if process is still running
            time.sleep(5)
            if process.poll() is not None:
                print("Error: Emulator crashed on startup.")
                print("Trying with different GPU mode...")
                
                # Try alternative GPU modes if first attempt fails
                gpu_modes = ['angle_indirect', 'guest', 'host']
                for gpu_mode in gpu_modes:
                    emulator_cmd[3] = gpu_mode
                    print(f"Attempting with -gpu {gpu_mode}...")
                    process = subprocess.Popen(emulator_cmd,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                    time.sleep(5)
                    if process.poll() is None:
                        print(f"Success with GPU mode: {gpu_mode}")
                        return process
                
                print("\nAll GPU modes failed. Please ensure:")
                print("1. Your system meets minimum requirements")
                print("2. Hardware virtualization is enabled in BIOS")
                print("3. GPU drivers are up to date")
                return None
                
            return process
            
        except Exception as e:
            print(f"Error launching emulator: {e}")
            return None

    # Install and launch app
    def install_app(apk_path):
        if not os.path.exists(apk_path):
            print(f"APK not found at: {apk_path}")
            return False
            
        try:
            print("Waiting for emulator to boot...")
            subprocess.run(['adb', 'wait-for-device'], check=True)
            
            # Wait for system to be ready
            while True:
                result = subprocess.run(
                    ['adb', 'shell', 'getprop', 'sys.boot_completed'],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip() == '1':
                    break
                time.sleep(2)
            
            print("Installing APK...")
            subprocess.run(['adb', 'install', '-r', apk_path], check=True)
            print("App installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing app: {e}")
            return False

    return {
        'launch': launch_emulator,
        'install_app': install_app
    }

if __name__ == "__main__":
    emulator = setup_pixel9_emulator()
    if emulator:
        emulator_process = emulator['launch']()
        if emulator_process:
            print("Emulator launched successfully!")
            # Uncomment and modify to install an APK:
            # emulator['install_app']('path/to/your/app.apk')