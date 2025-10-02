# Calibration Buttons Comparison Guide

## Overview of the Three Calibration Methods

The Parameters tab (Advanced Parameters) has three different calibration buttons. Here's what each one does:

---

## 1. 🧮 Create Calibration from Standards

### What It Does
Creates a calibration for **ONE element** by **manually entering** integrated intensities.

### Workflow
1. Select an element from the dropdown (e.g., Pb, Zn, Cu)
2. Click "🧮 Create Calibration from Standards"
3. Dialog shows available reference materials for that element
4. **YOU manually enter** the integrated intensity for each standard
5. System creates calibration curve from your entered values

### When to Use
- You've already analyzed the spectra elsewhere
- You have integrated intensity values from another software
- You want to manually input specific intensity values
- You're doing quality control with known intensity values

### Example
For Lead (Pb):
- You select "Pb" from dropdown
- Click the button
- Dialog shows: NIST 2586 (432 ppm), NIST 2587 (3242 ppm), etc.
- You type in intensity values:
  - NIST 2586: 13,100 cps
  - NIST 2587: 98,500 cps
  - etc.
- System calculates: Concentration = slope × Intensity + intercept

### Key Features
- ✅ **Manual input** of intensities
- ✅ **Single element** at a time
- ✅ Quick if you already have intensity values
- ❌ Requires you to analyze spectra separately

---

## 2. 🤖 Auto-Calibrate Current Element

### What It Does
Creates a calibration for **ONE element** by **automatically analyzing** XRF spectrum files.

### Workflow
1. Select an element from the dropdown (e.g., Pb, Zn, Cu)
2. Click "🤖 Auto-Calibrate Current Element"
3. Dialog shows available reference materials for that element
4. **YOU select XRF spectrum files** for each standard
5. System automatically:
   - Loads each spectrum file
   - Fits the peak for that element
   - Calculates integrated intensity
   - Creates calibration curve

### When to Use
- You have XRF spectrum files for your standards
- You want the system to do the peak fitting automatically
- You're working with one element at a time
- You want to see detailed results for each standard

### Example
For Zinc (Zn):
- You select "Zn" from dropdown
- Click the button
- Dialog shows: Till 1, LKSD 1, PACS 2, etc.
- You select files:
  - Till 1 → "Till1_spectrum.txt"
  - LKSD 1 → "LKSD1_spectrum.txt"
  - etc.
- System analyzes each file, fits Zn peak, creates calibration

### Key Features
- ✅ **Automatic peak fitting** and integration
- ✅ **Single element** at a time
- ✅ You just select files, system does the analysis
- ✅ Shows detailed fit results for each standard
- ❌ Only calibrates one element per run

---

## 3. 🚀 Auto-Calibrate ALL Elements

### What It Does
Creates calibrations for **ALL elements** (up to 10) by **automatically analyzing** XRF spectrum files.

### Workflow
1. Click "🚀 Auto-Calibrate ALL Elements" (no need to select element first)
2. System identifies which elements have enough standards (≥2)
3. Dialog shows ALL reference materials needed
4. **YOU select ONE spectrum file per reference material**
5. System automatically:
   - Analyzes ALL elements in EACH file
   - Fits peaks for Pb, Zn, Cu, Fe, etc. in each spectrum
   - Creates calibration curves for ALL elements simultaneously
6. **NEW FEATURES** (just added):
   - ✅ Checkboxes to select which standards to use
   - ✅ Add custom standards with your own concentrations

### When to Use
- You want to calibrate multiple elements at once
- You have spectrum files for reference materials
- You want the most efficient workflow
- You're setting up the system for the first time
- You want to use custom standards or select specific standards

### Example
Full multi-element calibration:
- Click "🚀 Auto-Calibrate ALL Elements"
- System shows: "Can calibrate 8 elements: Pb, Zn, Cu, Fe, Ni, Cr, As, Se"
- You see list of standards: NIST 2586, NIST 2587, Till 1, etc.
- **Check/uncheck** which standards you want to use
- **Add custom standards** if you have them
- Select ONE file per standard:
  - NIST 2586 → "NIST2586_spectrum.txt"
  - NIST 2587 → "NIST2587_spectrum.txt"
  - Custom Std → "MyStandard_spectrum.txt"
- System analyzes:
  - Pb peak in each file → creates Pb calibration
  - Zn peak in each file → creates Zn calibration
  - Cu peak in each file → creates Cu calibration
  - etc.
- Result: 8 calibrations created from one workflow!

### Key Features
- ✅ **Calibrates ALL elements** at once
- ✅ **Automatic peak fitting** for all elements
- ✅ **Most efficient** - one file per standard, multiple calibrations
- ✅ **Select which standards** to use (checkboxes)
- ✅ **Add custom standards** with your own concentrations
- ✅ Shows progress for each element
- ⚠️ Requires more reference materials (needs standards for multiple elements)

---

## Quick Comparison Table

| Feature | Create from Standards | Auto-Calibrate Current | Auto-Calibrate ALL |
|---------|----------------------|------------------------|-------------------|
| **Elements** | 1 element | 1 element | ALL elements (up to 10) |
| **Input Method** | Manual intensities | Select spectrum files | Select spectrum files |
| **Peak Fitting** | No (you provide values) | Yes (automatic) | Yes (automatic) |
| **Files Needed** | None | One per standard | One per standard |
| **Efficiency** | Fast if you have values | Medium | **Highest** |
| **Custom Standards** | No | No | **Yes** ✅ |
| **Select Standards** | No | No | **Yes** ✅ |
| **Best For** | Quick manual entry | Single element focus | Complete system setup |

---

## Recommendations

### Use "Create Calibration from Standards" when:
- You already have integrated intensity values
- You're importing data from another system
- You need to quickly update one element's calibration
- You're doing QC with known reference values

### Use "Auto-Calibrate Current Element" when:
- You're focusing on one specific element
- You want to see detailed fit results for that element
- You're troubleshooting calibration for one element
- You want step-by-step control

### Use "Auto-Calibrate ALL Elements" when:
- **Setting up the system for the first time** ⭐
- You want to calibrate multiple elements efficiently
- You have limited standards and want to select which to use
- You have custom/in-house standards to add
- You want the most comprehensive calibration workflow
- **This is the RECOMMENDED method for most users** ⭐

---

## Workflow Efficiency Example

### Scenario: Calibrate Pb, Zn, and Cu

**Method 1 - Create from Standards:**
- Select Pb → Enter 5 intensity values
- Select Zn → Enter 5 intensity values  
- Select Cu → Enter 5 intensity values
- **Total: 3 separate workflows, 15 manual entries**

**Method 2 - Auto-Calibrate Current:**
- Select Pb → Choose 5 files → Analyze
- Select Zn → Choose 5 files → Analyze
- Select Cu → Choose 5 files → Analyze
- **Total: 3 separate workflows, 15 file selections**

**Method 3 - Auto-Calibrate ALL:**
- Click once → Choose 5 files (one per standard)
- System analyzes Pb, Zn, AND Cu in each file
- **Total: 1 workflow, 5 file selections** ⭐
- **Plus: Can add custom standards and select which to use!**

---

## Summary

- **🧮 Create Calibration from Standards** = Manual entry, one element
- **🤖 Auto-Calibrate Current Element** = Automatic analysis, one element  
- **🚀 Auto-Calibrate ALL Elements** = Automatic analysis, all elements, most powerful ⭐

**For most users, "Auto-Calibrate ALL Elements" is the best choice** because it:
1. Calibrates multiple elements at once
2. Automatically fits all peaks
3. Lets you select which standards to use
4. Allows custom standards
5. Saves the most time

---

**Version:** 1.0  
**Last Updated:** October 2025
