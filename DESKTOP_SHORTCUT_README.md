# Desktop Shortcut Installation Guide

## Quick Start

Run the installer script:

```bash
python install_desktop_shortcut.py
```

This will create a desktop shortcut for the XRF Peak Fitting application on your desktop!

## What It Does

### macOS (Your System)
Creates **"XRF Peak Fitting.app"** on your desktop:
- Native macOS application bundle
- Double-click to launch
- Looks like a regular Mac app
- Includes Info.plist for proper macOS integration

### Windows
Creates **"XRF Peak Fitting.bat"** on the desktop:
- Batch file that launches the Python script
- Double-click to run
- Opens in a command window

### Linux
Creates **"xrf-peak-fitting.desktop"** on the desktop:
- Standard Linux desktop entry
- Integrates with application menu
- Double-click to launch

## First-Time Setup (macOS)

When you first double-click the app, macOS may show a security warning:

**"XRF Peak Fitting.app cannot be opened because it is from an unidentified developer"**

**Solution:**
1. Right-click (or Control+click) on the app
2. Select "Open" from the menu
3. Click "Open" in the dialog
4. The app will launch and remember this choice

This only needs to be done once!

## Customizing the Icon

### macOS

**Option 1: Use an existing icon**
1. Find an .icns icon file (e.g., from /System/Library/CoreServices/)
2. Copy it to: `XRF Peak Fitting.app/Contents/Resources/AppIcon.icns`
3. Restart Finder (or log out/in)

**Option 2: Create custom icon**
1. Create a 1024x1024 PNG image
2. Use online converter to create .icns file (e.g., cloudconvert.com)
3. Place in Resources folder as above

**Option 3: Use app icon**
1. Right-click any app with an icon you like
2. Get Info (Cmd+I)
3. Click the icon in top-left
4. Copy (Cmd+C)
5. Get Info on XRF Peak Fitting.app
6. Click its icon and Paste (Cmd+V)

### Windows

1. Right-click the .bat file
2. Select "Properties"
3. Click "Change Icon"
4. Browse to an .ico file or select from system icons
5. Click OK

### Linux

1. Edit the .desktop file
2. Change the `Icon=` line to point to your icon file
3. Save and close

## Icon Suggestions

**Science/Chemistry themed:**
- 🧪 Test tube / beaker
- 📊 Graph / chart
- ⚛️ Atom symbol
- 🔬 Microscope
- 📈 Analytics

**Where to find icons:**
- macOS: `/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/`
- Free icons: flaticon.com, icons8.com
- Create your own: Use Preview or GIMP

## Troubleshooting

### macOS: "App is damaged and can't be opened"

**Solution:**
```bash
xattr -cr ~/Desktop/XRF\ Peak\ Fitting.app
```

This removes the quarantine attribute.

### macOS: App doesn't launch

**Check:**
1. Python 3 is installed: `python3 --version`
2. Required packages installed: `pip install -r requirements.txt`
3. Script path is correct in the launcher

**Debug:**
```bash
# Run the launcher script directly to see errors
~/Desktop/XRF\ Peak\ Fitting.app/Contents/MacOS/launch_xrf
```

### Windows: "Python not found"

**Solution:**
1. Install Python from python.org
2. During installation, check "Add Python to PATH"
3. Restart computer
4. Try the shortcut again

### Linux: Desktop file doesn't work

**Solution:**
```bash
# Make it executable
chmod +x ~/Desktop/xrf-peak-fitting.desktop

# Mark as trusted (Ubuntu/GNOME)
gio set ~/Desktop/xrf-peak-fitting.desktop metadata::trusted true
```

## Uninstalling

Simply delete the shortcut from your desktop:

**macOS:**
```bash
rm -rf ~/Desktop/XRF\ Peak\ Fitting.app
```

**Windows:**
Delete `XRF Peak Fitting.bat` from desktop

**Linux:**
```bash
rm ~/Desktop/xrf-peak-fitting.desktop
```

## Advanced: Custom Installation Location

To install to a different location, edit the script:

```python
def get_desktop_path():
    # Change this to your desired location
    return Path("/path/to/your/location")
```

## Reinstalling

Just run the installer script again:
```bash
python install_desktop_shortcut.py
```

It will overwrite the existing shortcut.

## Distribution

To share the app with colleagues:

**macOS:**
1. Zip the entire .app bundle
2. Share the .zip file
3. They unzip and drag to their Desktop
4. They may need to right-click → Open first time

**Windows:**
1. Share the .bat file
2. They need to edit it to point to their Python installation
3. Or share the entire folder with requirements.txt

**Better approach:**
- Use PyInstaller to create standalone executables
- No Python installation needed
- Single .exe (Windows) or .app (macOS)

## Creating Standalone Executables (Future)

To create a standalone app that doesn't require Python:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "XRF Peak Fitting" xrf_Pb_analysis.py

# Find executable in dist/ folder
```

This creates a single file that anyone can run without installing Python!

## Summary

**Quick install:**
```bash
python install_desktop_shortcut.py
```

**Result:**
- ✅ Desktop shortcut created
- ✅ Double-click to launch
- ✅ Works on Windows, macOS, and Linux
- ✅ Easy to customize icon

**Your desktop now has:**
- macOS: "XRF Peak Fitting.app" 
- Windows: "XRF Peak Fitting.bat"
- Linux: "xrf-peak-fitting.desktop"

Just double-click to launch your XRF analysis application! 🚀

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Tested on:** macOS 14+, Windows 10+, Ubuntu 22.04+
