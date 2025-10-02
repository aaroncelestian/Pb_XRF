# Multi-Spectra Averaging for Calibration

## Overview

The calibration system now supports **multiple spectra per standard** with automatic averaging and error calculation. This provides:
- **Better calibration quality** through averaging
- **Error estimates** (standard deviation, RSD) for each standard
- **Quality metrics** to identify problematic measurements
- **Flexible file selection** via folder or individual file selection

## Why Use Multiple Spectra?

### Benefits
1. **Reduced Random Error** - Averaging multiple measurements reduces noise
2. **Error Quantification** - Calculate standard deviation and RSD for each standard
3. **Quality Assessment** - Identify outliers and problematic spectra
4. **Statistical Confidence** - Know the precision of your calibration points
5. **Better R² Values** - More reliable calibration curves

### Example
**Single spectrum per standard:**
- NIST 2586: 13,100 cps
- NIST 2587: 98,500 cps
- No error information

**Multiple spectra per standard:**
- NIST 2586: 13,150 ± 180 cps (RSD=1.4%, n=5)
- NIST 2587: 98,200 ± 1,200 cps (RSD=1.2%, n=5)
- Clear error estimates!

## How to Use

### Method 1: Folder Selection (Recommended)

**Best for:** All spectra for one standard in a dedicated folder

1. Click **"🚀 Auto-Calibrate ALL Elements"**
2. For each standard, click **"📁 Folder"** button
3. Select the folder containing all spectra for that standard
4. System automatically finds all XRF files (*.txt, *.csv, *.xlsx, *.dat, *.emsa, *.spc)
5. Status shows: "✓ 5 files from NIST2586_folder"

**Example folder structure:**
```
Standards/
├── NIST_2586/
│   ├── spectrum_001.txt
│   ├── spectrum_002.txt
│   ├── spectrum_003.txt
│   ├── spectrum_004.txt
│   └── spectrum_005.txt
├── NIST_2587/
│   ├── run1.txt
│   ├── run2.txt
│   └── run3.txt
└── Till_1/
    ├── measurement_a.txt
    └── measurement_b.txt
```

### Method 2: Individual File Selection

**Best for:** Spectra scattered across different locations

1. Click **"🚀 Auto-Calibrate ALL Elements"**
2. For each standard, click **"📄 Files"** button
3. Select multiple files (Ctrl+Click or Cmd+Click for multiple selection)
4. Status shows: "✓ 5 files selected"

### Method 3: Mixed Approach

You can mix both methods:
- Use **Folder** for standards with organized folders
- Use **Files** for standards with scattered spectra
- Some standards can have 1 file, others can have 10+ files

## What Happens During Analysis

### For Each Standard:

1. **Load all spectra files** for that standard
2. **Fit peaks** for all elements in each spectrum
3. **Calculate statistics:**
   - Mean intensity
   - Standard deviation
   - Relative Standard Deviation (RSD %)
   - Number of spectra (n)

4. **Display results:**
   ```
   🔬 Analyzing NIST 2586 (5 spectra)...
       Pb: 13,150 ± 180 cps (RSD=1.4%, n=5)
       Zn: 8,420 ± 95 cps (RSD=1.1%, n=5)
       Cu: 5,230 ± 140 cps (RSD=2.7%, n=5)
   ```

5. **Use mean values** for calibration curve

### Calibration Creation:

- Each standard contributes ONE point to the calibration curve
- That point is the **average** of all spectra for that standard
- Error information is displayed but not used in regression (future enhancement)

## Interpreting Results

### RSD (Relative Standard Deviation)

**What it means:**
- RSD = (Std Dev / Mean) × 100%
- Measures precision as a percentage

**Quality guidelines:**
- **RSD < 2%**: Excellent precision ✅
- **RSD 2-5%**: Good precision ✅
- **RSD 5-10%**: Acceptable, but check for issues ⚠️
- **RSD > 10%**: Poor precision, investigate! ❌

### Example Output

```
🔬 Analyzing NIST 2586 (5 spectra)...
    Pb: 13,150 ± 180 cps (RSD=1.4%, n=5)  ← Excellent!
    Zn: 8,420 ± 95 cps (RSD=1.1%, n=5)   ← Excellent!
    Cu: 5,230 ± 520 cps (RSD=9.9%, n=5)  ← Check this!
```

**Interpretation:**
- Pb and Zn measurements are very precise
- Cu has high variability - possible issues:
  - Low Cu concentration (near detection limit)
  - Inhomogeneous sample
  - Instrumental drift
  - One or more bad spectra

## Best Practices

### 1. Number of Spectra

**Minimum:** 1 spectrum per standard (works, but no error estimate)
**Recommended:** 3-5 spectra per standard (good balance)
**Optimal:** 5-10 spectra per standard (best statistics)
**Diminishing returns:** >10 spectra (time vs. benefit)

### 2. File Organization

**Option A - Organized folders (recommended):**
```
Calibration_2025-10-01/
├── NIST_2586/
├── NIST_2587/
├── Till_1/
└── LKSD_1/
```

**Option B - Naming convention:**
```
NIST2586_001.txt
NIST2586_002.txt
NIST2586_003.txt
NIST2587_001.txt
NIST2587_002.txt
```

### 3. Quality Control

**Before calibration:**
- Collect 3-5 spectra per standard
- Use consistent measurement conditions
- Check for sample homogeneity

**During calibration:**
- Review RSD values
- Investigate standards with RSD > 5%
- Consider excluding outlier spectra

**After calibration:**
- Check R² values (should be > 0.99)
- Review calibration plots
- Validate with known samples

### 4. Troubleshooting High RSD

If you see high RSD (>5%) for a standard:

1. **Check individual spectra** - Are they all similar?
2. **Look for outliers** - One bad spectrum can skew results
3. **Sample issues** - Inhomogeneous? Contaminated?
4. **Instrumental** - Drift? Positioning issues?
5. **Low concentration** - Near detection limit?

**Solutions:**
- Exclude bad spectra (use Files selection, not Folder)
- Re-measure the standard
- Use different standard if available
- Accept higher uncertainty for that point

## Advanced Features

### Custom Standards with Multiple Spectra

Custom standards also support multiple spectra:

1. Add custom standard with concentrations
2. Use **Folder** or **Files** button
3. Select multiple spectra
4. System averages automatically

### Selective Standard Usage

Combine with checkbox selection:
- Check only standards with good RSD
- Uncheck standards with problematic measurements
- Create calibration with high-quality data only

## Technical Details

### Statistics Calculated

For each standard and element:
```python
intensities = [I1, I2, I3, ..., In]  # From n spectra
mean = np.mean(intensities)
std = np.std(intensities, ddof=1)    # Sample std dev
rsd = (std / mean) * 100             # Relative std dev %
```

### File Format Support

Automatically detects and loads:
- *.txt (text files)
- *.csv (comma-separated)
- *.xlsx (Excel)
- *.dat (data files)
- *.emsa (EMSA format)
- *.spc (SPC format)

### Memory Efficiency

- Files are loaded one at a time
- Only intensities are stored in memory
- Suitable for hundreds of spectra

## Example Workflow

### Scenario: Calibrate Pb and Cr

**Your data:**
- NIST 2586: 5 spectra in folder
- NIST 2587: 3 spectra in folder
- Till 1: 4 individual files

**Steps:**

1. Click "🚀 Auto-Calibrate ALL Elements"

2. NIST 2586:
   - Click "📁 Folder"
   - Select "NIST_2586" folder
   - Status: "✓ 5 files from NIST_2586"

3. NIST 2587:
   - Click "📁 Folder"
   - Select "NIST_2587" folder
   - Status: "✓ 3 files from NIST_2587"

4. Till 1:
   - Click "📄 Files"
   - Select 4 files with Ctrl+Click
   - Status: "✓ 4 files selected"

5. Click "🚀 Analyze Selected Standards & Create Calibrations"

6. **Results:**
   ```
   🔬 Analyzing NIST 2586 (5 spectra)...
       Pb: 13,150 ± 180 cps (RSD=1.4%, n=5)
       Cr: 2,840 ± 65 cps (RSD=2.3%, n=5)
   
   🔬 Analyzing NIST 2587 (3 spectra)...
       Pb: 98,200 ± 1,200 cps (RSD=1.2%, n=3)
       Cr: 21,500 ± 480 cps (RSD=2.2%, n=3)
   
   🔬 Analyzing Till 1 (4 spectra)...
       Pb: 45,600 ± 920 cps (RSD=2.0%, n=4)
       Cr: 12,300 ± 310 cps (RSD=2.5%, n=4)
   
   📊 Creating calibration curves...
   ✅ Pb: y = 0.0329x + 2.1, R² = 0.9998
       Standards used: NIST 2586, NIST 2587, Till 1
   ✅ Cr: y = 0.0451x + 1.8, R² = 0.9997
       Standards used: NIST 2586, NIST 2587, Till 1
   ```

7. **Excellent calibrations!** All RSD < 3%, R² > 0.999

## Future Enhancements

Potential additions:
- Weighted regression using error estimates
- Outlier detection and automatic exclusion
- Error propagation to final concentrations
- Uncertainty budgets
- Graphical display of individual measurements

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Compatible with:** XRF Multi-Element Analysis v2.0+
