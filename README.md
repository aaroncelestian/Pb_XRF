# XRF_Pb: XRF Peak Fitting and Quantitative Analysis

## Overview
Born from the Prospering backyards (Pb) project, XRF_Pb is a user-friendly desktop application for batch and single-file X-ray fluorescence (XRF) analysis of lead (Pb) in pressed pellets. It provides robust peak fitting, background subtraction, NIST-based calibration, and comprehensive reporting for laboratory and research use.

## Features
- **Batch and Single Spectrum Analysis**
- **Gaussian-A-Peak Fitting** with linear background subtraction
- **NIST Calibration** for quantitative Pb concentration
- **Interactive Qt GUI** (PySide6)
- **Spectrum Browser** for reviewing individual fits
- **Automatic and Exportable Sample Statistics**
- **Customizable Fitting Parameters**
- **PDF, HTML, and Word Report Generation**
- **Markdown SOP Viewer**

## Installation

You can set up the application in one of two ways, depending on your comfort level.

### Option A — Download ZIP (no Git required)
1. Download the project ZIP from GitHub:
   - Click the green "Code" button on the repository page and choose "Download ZIP".
   - Extract the ZIP (e.g., to your Desktop) and remember the folder location.
2. Install Python (Anaconda recommended):
   - Download Anaconda from the official site: https://www.anaconda.com/download
   - Run the installer and follow prompts.
3. Install required Python packages:
   - Open Command Prompt (Windows) or Terminal (macOS/Linux).
   - Navigate to the extracted folder (example):
     - Windows: `cd %USERPROFILE%\Desktop\XRF_Pb-main`
     - macOS/Linux: `cd ~/Desktop/XRF_Pb-main`
   - Install dependencies: `pip install -r requirements.txt`

### Option B — Git + Conda environment (recommended for developers)
1. Clone the repository:
   ```bash
   git clone https://github.com/aaroncelestian/Pb_XRF.git
   cd Pb_XRF
   ```
2. Create and activate a dedicated environment (via conda):
   ```bash
   conda create -n xrf_env python=3.10
   conda activate xrf_env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Test your installation
Run the application from the project folder:
```bash
python xrf_Pb_analysis.py
```
If successful, a window will open with the XRF analysis application.

## Usage

### Starting the Application
1. Open Command Prompt (Windows) or Terminal (macOS/Linux).
2. Navigate to the project folder.
3. Run: `python xrf_Pb_analysis.py`

### Using the Application
- **Load Data:** Select single files or entire folders for batch analysis.
- **Adjust Settings:** Modify fitting and calibration parameters as needed.
- **Review Results:** Browse individual spectrum fits and view statistical summaries.
- **Generate Reports:** Export results and create PDF, HTML, or Word reports from the Docs/Export tab.

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
