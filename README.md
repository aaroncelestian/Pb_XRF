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

---

© 2025 Natural History Museum of Los Angeles County. All rights reserved. 
