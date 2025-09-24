# XRF_Pb: XRF Peak Fitting and Quantitative Analysis

## Overview
Born from the Prospering backyards (Pb) project, XRF_Pb is a user-friendly desktop application for batch and single-file X-ray fluorescence (XRF) analysis of lead (Pb) in pressed pellets. It provides robust peak fitting, background subtraction, NIST-based calibration, and comprehensive reporting for laboratory and research use.

## Features
- **Batch and Single Spectrum Analysis**
- **Gaussian-A Peak Fitting** with linear background subtraction
- **NIST Calibration** for quantitative Pb concentration
- **Interactive Qt GUI** (PySide6)
- **Spectrum Browser** for reviewing individual fits
- **Automatic and Exportable Sample Statistics**
- **Customizable Fitting Parameters**
- **PDF, HTML, and Word Report Generation**
- **Markdown SOP Viewer**

<<<<<<< HEAD
## Installation

### Step 1: Install Anaconda (Python Distribution)

**What is Anaconda?** Anaconda is a free software package that includes Python and many useful tools for scientific computing. Think of it as a complete toolkit that makes it easy to run Python programs on your computer.

#### For Windows Users:
1. **Download Anaconda:**
   - Go to [https://www.anaconda.com/download](https://www.anaconda.com/download)
   - Click the large "Download" button (it will automatically detect you're using Windows)
   - Wait for the file to download (it's about 500MB, so it may take a few minutes)

2. **Install Anaconda:**
   - Find the downloaded file (usually in your Downloads folder) - it will be named something like `Anaconda3-2024.02-1-Windows-x86_64.exe`
   - Double-click the file to start the installer
   - Click "Next" through the setup screens
   - **Important:** When asked about "Add Anaconda to PATH", check the box (even though it says "Not recommended")
   - Continue clicking "Next" and then "Install"
   - Wait for installation to complete (this takes 5-10 minutes)
   - Click "Finish" when done

#### For Mac Users:
1. **Download Anaconda:**
   - Go to [https://www.anaconda.com/download](https://www.anaconda.com/download)
   - Click the "Download" button for Mac
   - Wait for the file to download

2. **Install Anaconda:**
   - Find the downloaded file (usually in your Downloads folder) - it will be named something like `Anaconda3-2024.02-1-MacOSX-x86_64.pkg`
   - Double-click the file to start the installer
   - Follow the installation prompts by clicking "Continue" and "Install"
   - Enter your Mac password when prompted
   - Wait for installation to complete
   - Click "Close" when finished

### Step 2: Download the XRF_Pb Application

1. **Download this software:**
   - If you received this as a zip file, extract it to a folder on your Desktop
   - If you're downloading from GitHub:
     - Click the green "Code" button on the main page
     - Select "Download ZIP"
     - Extract the zip file to your Desktop

2. **Remember the location:** Make note of where you saved the folder (we recommend your Desktop for easy access)

### Step 3: Install Required Software Packages

**What are we doing?** We need to install additional software packages that the XRF application needs to work properly.

#### For Windows:
1. **Open Command Prompt:**
   - Press the Windows key + R
   - Type `cmd` and press Enter
   - A black window will open - this is the Command Prompt

2. **Navigate to your XRF folder:**
   - Type: `cd Desktop\XRF_Pb-main` (or whatever your folder is named)
   - Press Enter

3. **Install the required packages:**
   - Type: `pip install -r requirements.txt`
   - Press Enter
   - Wait for installation to complete (this takes 2-5 minutes)

#### For Mac:
1. **Open Terminal:**
   - Press Command + Space to open Spotlight search
   - Type "Terminal" and press Enter
   - A window with text will open - this is the Terminal

2. **Navigate to your XRF folder:**
   - Type: `cd Desktop/XRF_Pb-main` (or whatever your folder is named)
   - Press Enter

3. **Install the required packages:**
   - Type: `pip install -r requirements.txt`
   - Press Enter
   - Wait for installation to complete (this takes 2-5 minutes)

### Step 4: Test Your Installation

1. **Make sure you're still in the XRF folder** (from Step 3 above)

2. **Run the application:**
   - Type: `python xrf_Pb_analysis.py`
   - Press Enter

3. **Success!** If everything worked correctly, you should see a window open with the XRF analysis application.

### Troubleshooting

**If you get an error saying "python is not recognized" or "command not found":**
- **Windows:** You may need to restart your computer after installing Anaconda
- **Mac:** Try using `python3` instead of `python`

**If you get errors about missing packages:**
- Make sure you completed Step 3 successfully
- Try running the pip install command again

**If the application window doesn't open:**
- Check that you're in the correct folder (the one containing `xrf_Pb_analysis.py`)
- Make sure all the installation steps completed without errors

**Need help?** Contact Aaron Celestian at acelestian@nhm.org with a description of any error messages you see.

## Usage

### Starting the Application
Once you've completed the installation steps above, you can start the XRF analysis application by:
1. Opening Command Prompt (Windows) or Terminal (Mac)
2. Navigating to your XRF folder: `cd Desktop/XRF_Pb-main`
3. Running: `python xrf_Pb_analysis.py`

### Using the Application
The application provides an easy-to-use graphical interface where you can:
- **Load Data:** Select single files or entire folders for batch analysis
- **Adjust Settings:** Modify fitting and calibration parameters as needed
- **Review Results:** Browse through individual spectrum fits and view statistical summaries
- **Generate Reports:** Export results and create PDF, HTML, or Word reports from the Docs/Export tab

### Quick Start Guide
1. Click "Browse" to select your XRF data files
2. Click "Analyze" to start the analysis
3. Review the results in the spectrum browser
4. Export your results using the "Docs/Export" tab
=======
# XRF Data Analysis Program

This program is designed to help you analyze X-ray fluorescence (XRF) data efficiently and reliably.

## Installation Instructions

Follow these steps to install and set up the environment for the XRF Data Analysis Program.

### 1. Install Anaconda

If you don't already have Anaconda installed, download and install it from the [official Anaconda website](https://www.anaconda.com/products/distribution).

#### For Windows/MacOS/Linux:

- Download the installer for your OS.
- Run the installer and follow the prompts.

### 2. Clone the Repository

Open your terminal or Anaconda Prompt (windows), and run:

```
git clone https://github.com/aaroncelestian/Pb_XRF.git
cd Pb_XRF
```

### 3. Create and Activate a Conda Environment

It's recommended to use a new conda environment to manage dependencies.

```
conda create -n xrf_env python=3.10
conda activate xrf_env
```

### 4. Install Required Packages

Install the dependencies listed in `requirements.txt`:

```
pip install -r requirements.txt
```

### 5. Run the Program

Run the main script (replace `main.py` with the entry point of your program if different):

```bash
python main.py
```

## Example Terminal Commands

```bash
# Download repository
git clone https://github.com/aaroncelestian/Pb_XRF.git
cd Pb_XRF

# Create new environment
conda create -n xrf_env python=3.10
conda activate xrf_env

# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
```

## Additional Notes

- Make sure you have [Git](https://git-scm.com/) installed.
- If you encounter issues with dependencies, check the `requirements.txt` or `environment.yml` for specific versions.
- For additional help, refer to the documentation or open an issue in the repository.

---
Happy analyzing!

## Usage
1. Run the application:
   ```   python xrf_Pb_analysis.py
   ```
2. Use the GUI to:
   - Select single files or folders for batch analysis
   - Adjust fitting and calibration parameters as needed
   - Review results in the spectrum browser and statistics plots
   - Export results and generate reports from the Docs/Export tab
>>>>>>> a9337515d63086c91d377d90c2861065f50eb64a

## File Formats Supported
- `.txt`, `.csv`, `.xlsx`, `.dat`, `.emsa`, `.spc` (auto-detected)

## Project Structure
- `xrf_Pb_analysis.py` — Main application
- `matplotlib_config.py` — Custom matplotlib style
- `synthetic_data/` — Example data files
- `xrf_sop_markdown.md` — Standard Operating Procedure (SOP)
- `requirements.txt` — Python dependencies

## Additional Troubleshooting

### Common Issues and Solutions

**Font or Qt warnings when running the application:**
- These warning messages are usually harmless and don't affect the application's functionality
- You can safely ignore them - the application should still work normally

**PDF or Word export not working:**
- The required packages (`reportlab` and `python-docx`) should be installed automatically with the requirements.txt file
- If exports still don't work, try reinstalling: `pip install reportlab python-docx`

**Application runs slowly:**
- This is normal for large datasets or batch processing
- Be patient and let the analysis complete
- You can monitor progress in the application's status bar

**Can't find your data files:**
- Make sure your XRF data files are in a supported format: `.txt`, `.csv`, `.xlsx`, `.dat`, `.emsa`, or `.spc`
- Check that the file path doesn't contain special characters or very long names

### Getting Additional Help
If you encounter issues not covered here:
1. Note down any error messages exactly as they appear
2. Include information about your operating system (Windows/Mac) and version
3. Contact Aaron Celestian at acelestian@nhm.org for assistance

## Contact
For questions, bug reports, or feature requests, contact:

**Aaron Celestian**  
Email: acelestian@nhm.org

---

© 2025 Natural History Museum of Los Angeles County. All rights reserved. 
