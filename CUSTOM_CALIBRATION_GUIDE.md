# Custom Calibration Guide - XRF Pb Analysis

## Overview

The XRF Pb Analysis software now includes a **Custom Calibration Manager** that allows you to create your own calibration curves using NIST Standard Reference Materials (SRMs). This is particularly useful when you have measured your own standards and want to use them instead of the default NIST calibration.

## Supported Standards

The system is designed to work with NIST lead standards, particularly:
- **SRM 2586** - 432 ppm Pb
- **SRM 2587** - 3242 ppm Pb

You can also add other standards with known concentrations.

## Getting Started

### 1. Accessing the Custom Calibration Manager

1. Open the XRF Analysis software
2. Go to **Advanced Parameters** tab
3. In the **Calibration Parameters** section, click **🧪 Create Custom Calibration**

### 2. Preparing Your Standard Files

Before starting, ensure you have:
- XRF spectrum files for each standard (3 files per standard recommended)
- Files should be in supported formats: `.txt`, `.csv`, `.xlsx`, `.dat`, `.emsa`, `.spc`
- Files should contain energy (keV) and intensity (counts) data

## Step-by-Step Calibration Process

### Step 1: Standards Setup

1. **Load Standard Files**:
   - In the **Standards Setup** tab, you'll see sections for SRM 2586 and SRM 2587
   - Click **Add Files** for each standard
   - Select your XRF spectrum files (3 files per standard recommended)
   - Files will appear in the list for each standard

2. **Verify File Loading**:
   - Check that files are listed correctly
   - Use **Remove Selected** or **Clear All** if you need to modify the file list

### Step 2: Analysis

1. **Run Analysis**:
   - Click **🔬 Analyze All Standards**
   - The system will process each file using your current fitting parameters
   - A progress dialog will show analysis status
   - Results appear in the text boxes below each standard

2. **Review Individual Results**:
   - Each standard shows:
     - Number of files analyzed
     - Mean integrated intensity
     - Standard deviation and RSD
     - Expected concentration

### Step 3: Calibration Results

1. **View Calibration Equation**:
   - Switch to **Calibration Results** tab
   - The calibration equation is displayed: `Concentration = slope × Intensity + intercept`
   - Statistics show R-squared, individual standard results, and errors

2. **Examine Calibration Plot**:
   - Visual plot shows your standards as data points
   - Custom calibration line in red
   - Comparison with current NIST calibration in green (dashed)
   - R-squared value indicates quality of fit

### Step 4: Validation

1. **Check Validation Results**:
   - Switch to **Validation** tab
   - R-squared quality assessment:
     - ✅ EXCELLENT: R² ≥ 0.995
     - ✅ GOOD: R² ≥ 0.99
     - ⚠️ ACCEPTABLE: R² ≥ 0.98
     - ❌ POOR: R² < 0.98

2. **Standard Recovery**:
   - Shows how well each standard recovers its expected concentration
   - Target: 95-105% recovery

3. **Precision Assessment**:
   - RSD for replicate measurements of each standard
   - Target: RSD ≤ 5%

### Step 5: Apply Calibration

1. **Save Calibration** (Optional):
   - Click **💾 Save Calibration** to save your work
   - Creates a `.json` file with all calibration data
   - Can be loaded later with **📂 Load Calibration**

2. **Apply to Analysis**:
   - Click **✅ Apply Calibration**
   - Confirms replacement of current calibration
   - Updates all subsequent analyses

## Quality Guidelines

### Minimum Requirements
- **At least 2 standards** with known concentrations
- **R-squared ≥ 0.98** for acceptable calibration
- **Standard recovery**: 90-110% (95-105% preferred)
- **Precision**: RSD ≤ 10% (≤5% preferred)

### Best Practices
- Use **3+ replicate files** per standard for better statistics
- Standards should **span your concentration range of interest**
- Check **fitting parameters** are optimized before analysis
- **Verify peak identification** - ensure you're fitting the Pb L-alpha peak
- **Document your standards** - keep records of preparation and analysis dates

## Troubleshooting

### Poor R-squared (< 0.98)
**Possible Causes:**
- Insufficient number of standards
- Wide scatter in replicate measurements
- Peak fitting issues
- Matrix effects between standards

**Solutions:**
- Add more standards across concentration range
- Check replicate precision (RSD should be <5%)
- Optimize fitting parameters (peak region, integration region)
- Verify standard preparation consistency

### High RSD in Standards (> 5%)
**Possible Causes:**
- Sample inhomogeneity
- Instrumental drift
- Peak fitting instability
- Beam positioning variations

**Solutions:**
- Re-prepare pellets with better mixing
- Check instrument stability
- Optimize fitting parameters
- Use longer count times
- Check beam alignment

### Poor Standard Recovery (outside 95-105%)
**Possible Causes:**
- Incorrect standard concentrations
- Matrix effects
- Systematic errors in preparation

**Solutions:**
- Verify standard certificate values
- Check pellet preparation protocol
- Ensure consistent sample preparation
- Consider matrix-matched standards

## Example Workflow with Your Standards

### For SRM 2586 (432 ppm):
1. Load 3 XRF files of SRM 2586 pellets
2. System analyzes each file, extracts integrated intensities
3. Calculates mean intensity for 432 ppm point

### For SRM 2587 (3242 ppm):
1. Load 3 XRF files of SRM 2587 pellets  
2. System analyzes each file, extracts integrated intensities
3. Calculates mean intensity for 3242 ppm point

### Calibration Creation:
1. Linear regression through both points: (intensity₁, 432) and (intensity₂, 3242)
2. Equation: Concentration = slope × Intensity + intercept
3. R-squared calculated to assess linearity

## Comparison with Default NIST Calibration

The system will show you:
- **Slope differences**: How much your calibration differs
- **Intercept differences**: Offset between calibrations  
- **Test concentrations**: Predicted values at different intensity levels
- **Visual comparison**: Both calibration lines on the same plot

## File Management

### Saving Calibrations
- Saves as JSON format with all data
- Includes calibration equation, standards data, and metadata
- Can be shared between users or systems

### Loading Calibrations
- Restores complete calibration state
- Updates all displays and enables Apply button
- Maintains traceability to original standards

## Advanced Features

### Multiple Standards
While designed for SRM 2586 and SRM 2587, you can:
- Modify concentration values if using different standards
- Add data points manually (advanced users)
- Create calibrations spanning different concentration ranges

### Validation Tests
- Statistical assessment of calibration quality
- Individual standard recovery analysis
- Precision assessment for replicate measurements
- Overall recommendation for calibration use

## Integration with Analysis Workflow

Once applied, your custom calibration:
- **Replaces the default NIST calibration** for all subsequent analyses
- **Updates the calibration verification plot** with "Custom Calibration" label
- **Maintains all existing functionality** - batch processing, reporting, etc.
- **Preserves absolute intensity values** - only changes the concentration calculation

## Benefits of Custom Calibration

1. **Instrument-Specific**: Tailored to your specific XRF instrument and setup
2. **Matrix-Matched**: Uses the same sample preparation as your unknowns
3. **Traceable**: Direct connection to your measured standards
4. **Current**: Reflects current instrument performance
5. **Validated**: Built-in quality checks and validation tests

---

**Result**: Your XRF analysis now uses calibration parameters derived from your own measurements of NIST standards, providing improved accuracy and traceability for your specific analytical setup. 