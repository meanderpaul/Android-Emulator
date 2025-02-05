# Android Emulator Setup for Cursor

A streamlined setup for Android development using Cursor IDE and Android Emulator.

## Table of Contents
- [Initial Setup](#initial-setup)
- [Cursor Configuration](#cursor-configuration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Updates and Maintenance](#updates-and-maintenance)

## Initial Setup

### System Requirements
- Windows 10/11
- 8GB RAM minimum (16GB recommended)
- Virtualization enabled in BIOS
- Administrator privileges

### Installation Steps
1. Run the Android Emulator program
2. Click "Setup/Update" and wait for completion:
   - Android SDK installation
   - Platform tools setup
   - Emulator configuration
3. Click "Setup for Cursor" to configure integration
4. Click "Launch Emulator" to start the Android device

## Cursor Configuration

### First-Time Setup
1. Open Cursor
2. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
3. Type "Android" to see available commands

### Creating a New Android Project
1. Command Palette → "Create Android Project"
2. Configure project settings:
```gradle
android {
    compileSdk 34
    
    defaultConfig {
        applicationId "your.package.name"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
}
```

### Configuring Existing Project
1. Open your project in Cursor
2. Verify build.gradle settings:
```gradle
android {
    namespace 'your.package.name'
    compileSdk 34

    defaultConfig {
        minSdk 24
        targetSdk 34
    }
}
```

## Development Workflow

### Running Your App
1. Ensure emulator is running
2. In Cursor:
   - Command Palette → "Run on Android Device"
   - Or use the play button (▶️) in the toolbar

### Debugging
1. Enable USB debugging in emulator:
   - Settings → About Phone
   - Tap "Build Number" 7 times
   - Settings → Developer Options
   - Enable "USB debugging"

2. Verify connection:
```bash
adb devices
```
Should show: `emulator-5554 device`

### Common ADB Commands
```bash
# List connected devices
adb devices

# Install APK
adb install path/to/app.apk

# View logs
adb logcat

# Copy files to device
adb push local/file /sdcard/

# Copy files from device
adb pull /sdcard/file local/

# Restart ADB server
adb kill-server
adb start-server
```

## Troubleshooting

### Common Issues and Solutions

1. **Emulator Not Starting**
   - Check virtualization is enabled in BIOS
   - Verify Windows Hypervisor Platform is enabled
   - Run as administrator

2. **ADB Connection Failed**
```bash
# Reset ADB
adb kill-server
adb start-server
```

3. **Build Errors**
   - Clean project:
```bash
./gradlew clean
```
   - Invalidate Cursor caches
   - Verify SDK paths

4. **Performance Issues**
   - Check GPU mode in preferences
   - Increase RAM allocation
   - Close unnecessary applications

### Error Messages

1. "INSTALL_FAILED_UPDATE_INCOMPATIBLE"
```bash
adb uninstall your.package.name
```

2. "ADB server didn't ACK"
   - Kill and restart ADB server
   - Check firewall settings

## Advanced Configuration

### Custom Emulator Settings
```bash
# Launch with custom settings
emulator -avd Pixel9Pro -gpu host -memory 2048 -cores 4
```

### Build Configuration
```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt')
        }
        debug {
            applicationIdSuffix ".debug"
            debuggable true
        }
    }
}
```

### Development Tools
1. Layout Inspector
   - Command Palette → "Android: Layout Inspector"
2. Database Inspector
   - Command Palette → "Android: Database Inspector"
3. Logcat
   - Command Palette → "Android: Logcat"

## Updates and Maintenance

### Keeping Updated
1. Run "Setup/Update" periodically
2. Update Cursor regularly
3. Check for emulator updates

### File Locations
- Android SDK: `~/Desktop/android tools`
- Cursor config: `~/.cursor/config/android.json`
- Emulator logs: `android_emulator.log`
- AVD data: `~/.android/avd/`

### Backup and Recovery
1. Export AVD settings:
```bash
avdmanager list avd > avd_backup.txt
```
2. Backup preferences:
```bash
cp ~/.cursor/config/android.json android_backup.json
```

## Support and Resources

### Official Documentation
- [Android Developer Guides](https://developer.android.com/guide)
- [Cursor Documentation](https://cursor.sh/docs)

### Community Support
- [Android Developers Forum](https://stackoverflow.com/questions/tagged/android)
- [Cursor Discord](https://discord.gg/cursor)

### Logging and Debugging
1. Check emulator logs:
```bash
cat android_emulator.log
```
2. Enable verbose logging:
```bash
adb shell setprop log.tag.YourTag VERBOSE
```

### Contact
For issues with the emulator setup:
1. Check the log file
2. Verify configurations
3. Contact support with log files

---

## License
This setup tool is provided under the MIT License.

## Contributing
Feel free to submit issues and enhancement requests.

## Version History
- 1.0.0: Initial release
- 1.0.1: Added Cursor integration
- 1.0.2: Performance improvements
```
