#!/usr/bin/env python3
"""
Desktop Shortcut Installer for XRF Peak Fitting Application
Creates desktop shortcuts on Windows, macOS, and Linux
"""

import os
import sys
import platform
import shutil
from pathlib import Path

def get_desktop_path():
    """Get the desktop path for the current OS"""
    system = platform.system()
    
    if system == "Windows":
        return Path.home() / "Desktop"
    elif system == "Darwin":  # macOS
        return Path.home() / "Desktop"
    elif system == "Linux":
        return Path.home() / "Desktop"
    else:
        return Path.home() / "Desktop"

def get_script_dir():
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()

def create_windows_shortcut():
    """Create a Windows .bat shortcut"""
    desktop = get_desktop_path()
    script_dir = get_script_dir()
    
    # Path to the main script
    main_script = script_dir / "xrf_Pb_analysis.py"
    
    # Create a .bat file
    shortcut_path = desktop / "XRF Peak Fitting.bat"
    
    bat_content = f'''@echo off
cd /d "{script_dir}"
python xrf_Pb_analysis.py
pause
'''
    
    with open(shortcut_path, 'w') as f:
        f.write(bat_content)
    
    print(f"✅ Windows shortcut created: {shortcut_path}")
    print(f"   Double-click 'XRF Peak Fitting.bat' on your desktop to launch the app")
    
    return shortcut_path

def create_macos_app():
    """Create a macOS .app bundle"""
    desktop = get_desktop_path()
    script_dir = get_script_dir()
    
    # Create .app bundle structure
    app_name = "XRF Peak Fitting.app"
    app_path = desktop / app_name
    
    # Remove existing app if it exists
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # Create directory structure
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>XRF Peak Fitting</string>
    <key>CFBundleDisplayName</key>
    <string>XRF Peak Fitting</string>
    <key>CFBundleIdentifier</key>
    <string>com.xrf.peakfitting</string>
    <key>CFBundleVersion</key>
    <string>2.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>XRFP</string>
    <key>CFBundleExecutable</key>
    <string>launch_xrf</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
'''
    
    with open(contents_dir / "Info.plist", 'w') as f:
        f.write(info_plist)
    
    # Create launcher script
    launcher_script = f'''#!/bin/bash
cd "{script_dir}"
python3 xrf_Pb_analysis.py
'''
    
    launcher_path = macos_dir / "launch_xrf"
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)
    
    # Make launcher executable
    os.chmod(launcher_path, 0o755)
    
    # Create a simple icon (text-based for now)
    # You can replace this with an actual .icns file later
    icon_script = '''#!/bin/bash
# Placeholder for icon
# To add a real icon, place an AppIcon.icns file in the Resources folder
'''
    
    with open(resources_dir / "README.txt", 'w') as f:
        f.write("To add a custom icon:\n")
        f.write("1. Create or download an .icns icon file\n")
        f.write("2. Name it 'AppIcon.icns'\n")
        f.write("3. Place it in this Resources folder\n")
    
    print(f"✅ macOS app created: {app_path}")
    print(f"   Double-click 'XRF Peak Fitting.app' on your desktop to launch")
    print(f"   Note: You may need to right-click → Open the first time (security)")
    
    return app_path

def create_linux_desktop_file():
    """Create a Linux .desktop file"""
    desktop = get_desktop_path()
    script_dir = get_script_dir()
    
    # Path to the main script
    main_script = script_dir / "xrf_Pb_analysis.py"
    
    # Create .desktop file
    shortcut_path = desktop / "xrf-peak-fitting.desktop"
    
    desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=XRF Peak Fitting
Comment=XRF Multi-Element Analysis Tool
Exec=python3 "{main_script}"
Path={script_dir}
Icon=utilities-terminal
Terminal=false
Categories=Science;Education;
'''
    
    with open(shortcut_path, 'w') as f:
        f.write(desktop_content)
    
    # Make it executable
    os.chmod(shortcut_path, 0o755)
    
    print(f"✅ Linux desktop file created: {shortcut_path}")
    print(f"   Double-click 'xrf-peak-fitting.desktop' to launch")
    print(f"   You may need to mark it as trusted first")
    
    return shortcut_path

def create_simple_icon():
    """Create a simple text-based icon representation"""
    # This is a placeholder - you can replace with actual icon creation
    # using PIL/Pillow if you want to generate actual image files
    pass

def main():
    """Main installation function"""
    print("=" * 60)
    print("XRF Peak Fitting - Desktop Shortcut Installer")
    print("=" * 60)
    print()
    
    system = platform.system()
    print(f"Detected OS: {system}")
    print(f"Desktop path: {get_desktop_path()}")
    print(f"Application path: {get_script_dir()}")
    print()
    
    try:
        if system == "Windows":
            print("Creating Windows shortcut...")
            create_windows_shortcut()
            
        elif system == "Darwin":  # macOS
            print("Creating macOS application bundle...")
            create_macos_app()
            
        elif system == "Linux":
            print("Creating Linux desktop file...")
            create_linux_desktop_file()
            
        else:
            print(f"⚠️  Unsupported operating system: {system}")
            print("   Please create a shortcut manually")
            return
        
        print()
        print("=" * 60)
        print("✅ Installation complete!")
        print("=" * 60)
        print()
        print("The XRF Peak Fitting application shortcut has been created")
        print("on your desktop. Double-click it to launch the application.")
        print()
        
        if system == "Darwin":
            print("macOS Note:")
            print("  If you see a security warning, right-click the app")
            print("  and select 'Open' to bypass Gatekeeper.")
            print()
        
        print("To customize the icon:")
        print("  - Windows: Right-click .bat file → Properties → Change Icon")
        print("  - macOS: Place an AppIcon.icns file in the app's Resources folder")
        print("  - Linux: Edit the .desktop file and set Icon= to your icon path")
        print()
        
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        print(f"   Please check permissions and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
