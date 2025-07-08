# XRF_Pb: XRF Peak Fitting and Quantitative Analysis for Lead (Pb)

## Overview
XRF_Pb is a user-friendly desktop application for batch and single-file X-ray fluorescence (XRF) analysis of lead (Pb) in pressed pellets. It provides robust peak fitting, background subtraction, NIST-based calibration, and comprehensive reporting for laboratory and research use.

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

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python xrf_Pb_analysis.py
   ```
2. Use the GUI to:
   - Select single files or folders for batch analysis
   - Adjust fitting and calibration parameters as needed
   - Review results in the spectrum browser and statistics plots
   - Export results and generate reports from the Docs/Export tab

## File Formats Supported
- `.txt`, `.csv`, `.xlsx`, `.dat`, `.emsa`, `.spc` (auto-detected)

## Project Structure
- `xrf_Pb_analysis.py` — Main application
- `matplotlib_config.py` — Custom matplotlib style
- `synthetic_data/` — Example data files
- `xrf_sop_markdown.md` — Standard Operating Procedure (SOP)
- `requirements.txt` — Python dependencies

## Troubleshooting
- If you see font or Qt warnings, they are usually harmless.
- For PDF/Word export, ensure `reportlab` and `python-docx` are installed.

## Contact
For questions, bug reports, or feature requests, contact:

**Aaron Celestian**  
Email: acelestian@nhm.org

## Screenshots

### Main Application Window
![Main Application Window](screenshots/main_window.png)

### PDF Report Example
![PDF Report Example](screenshots/pdf_report.png)

### SOP Viewer in Application
![SOP Viewer](screenshots/sop_viewer.png)

---

© 2025 Natural History Museum of Los Angeles County. All rights reserved. 