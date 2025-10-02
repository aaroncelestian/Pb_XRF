# Calibration Plots Tab Guide

## Overview

The **Calibration Plots** tab provides visual quality control for your element calibrations. It displays:
- **Calibration curves** for each element
- **Standard data points** plotted on the curve
- **Statistics table** showing certified vs. predicted concentrations
- **Color-coded accuracy** indicators

## Features

### 1. Visual Calibration Curves

**What you see:**
- Blue line: Calibration curve (Concentration = slope × Intensity + intercept)
- Red points: Reference standards used in calibration
- Labels: Standard names next to each point
- Grid: For easy reading of values

**Example:**
```
Lead (Pb) Calibration Curve
R² = 0.9998

Y-axis: Pb Concentration (ppm)
X-axis: Integrated Intensity (cps)

Points plotted:
- NIST 2586 (432 ppm)
- NIST 2587 (3242 ppm)
- Till 1 (1500 ppm)
```

### 2. Calibration Information Panel

Displays key calibration details:
- **Element name and symbol**
- **Calibration equation** with exact coefficients
- **R² value** (quality metric)
- **Standards used** in the calibration
- **Creation timestamp**

**Example:**
```
📊 Lead (Pb) Calibration
Equation: Concentration = 0.000329 × Intensity + 2.1
R² = 0.9998 | Standards: NIST 2586, NIST 2587, Till 1 | Created: 2025-10-01 19:30:15
```

### 3. Statistics Table

Shows detailed comparison for each standard:

| Standard | Certified (ppm) | Measured Intensity (cps) | Predicted (ppm) |
|----------|----------------|--------------------------|-----------------|
| NIST 2586 | 432.0 | 13,150 | 433.2 |
| NIST 2587 | 3242.0 | 98,200 | 3240.8 |
| Till 1 | 1500.0 | 45,600 | 1501.3 |

**Color coding:**
- 🟢 **Green**: Error < 2% (Excellent!)
- 🟡 **Yellow**: Error 2-5% (Good)
- 🔴 **Red**: Error > 5% (Check calibration)

### 4. Element Selector

- **Dropdown menu**: Select which element to view
- **Refresh button**: Update plot after creating new calibrations
- **Auto-update**: Plot refreshes when calibrations are created

## How to Use

### Basic Workflow

1. **Create calibrations** in the "Calibrations" tab first
   - Use "Auto-Calibrate ALL Elements" for best results

2. **Switch to "Calibration Plots" tab**

3. **Select element** from dropdown
   - Choose which element calibration to view

4. **Review the plot**
   - Check that R² is high (> 0.99)
   - Verify points lie close to the line
   - Look for outliers

5. **Check statistics table**
   - Green cells = good accuracy
   - Yellow/red cells = investigate

### Quality Control Checklist

✅ **R² Value**
- R² > 0.999: Excellent
- R² > 0.99: Good
- R² > 0.98: Acceptable
- R² < 0.98: Poor - recalibrate

✅ **Visual Inspection**
- Points should lie close to the line
- No obvious outliers
- Smooth, linear relationship

✅ **Predicted Concentrations**
- Should match certified values closely
- Most cells should be green
- Yellow cells acceptable
- Red cells need investigation

✅ **Standard Coverage**
- Standards should span expected concentration range
- At least 3 standards (more is better)
- Good distribution across range

## Interpreting Results

### Example 1: Excellent Calibration

```
📊 Lead (Pb) Calibration
Equation: Concentration = 0.000329 × Intensity + 2.1
R² = 0.9998

Plot shows:
- All points very close to line
- No outliers
- Good coverage of concentration range

Statistics table:
- All cells green
- Errors < 1%
```

**Action:** ✅ Calibration is excellent, ready to use!

### Example 2: Good Calibration with One Outlier

```
📊 Zinc (Zn) Calibration
Equation: Concentration = 0.000451 × Intensity + 1.8
R² = 0.9985

Plot shows:
- Most points close to line
- One point (PACS 2) slightly off

Statistics table:
- NIST 2586: Green (0.8% error)
- NIST 2587: Green (1.2% error)
- PACS 2: Yellow (3.5% error)
- Till 1: Green (1.5% error)
```

**Action:** ⚠️ Acceptable, but consider:
- Re-measuring PACS 2
- Checking PACS 2 sample quality
- Using more replicates for PACS 2

### Example 3: Poor Calibration

```
📊 Copper (Cu) Calibration
Equation: Concentration = 0.000823 × Intensity + 15.2
R² = 0.9650

Plot shows:
- Points scattered around line
- Large intercept (15.2 ppm)
- Non-zero intercept suggests issues

Statistics table:
- Multiple red cells
- Errors 5-15%
```

**Action:** ❌ Recalibrate:
- Check sample preparation
- Verify peak fitting quality
- Consider different standards
- Check for contamination

## Common Issues and Solutions

### Issue 1: "No calibration found"

**Message:** "⚠️ No calibration found for [Element]. Create a calibration in the Calibrations tab."

**Solution:**
1. Go to "Calibrations" tab
2. Click "Auto-Calibrate ALL Elements"
3. Follow calibration workflow
4. Return to "Calibration Plots" tab

### Issue 2: Low R² Value

**Symptoms:**
- R² < 0.99
- Points scattered around line

**Possible causes:**
- Poor quality spectra
- Inhomogeneous samples
- Wrong peak regions
- Contamination

**Solutions:**
- Collect more spectra per standard (use averaging)
- Check sample preparation
- Verify peak fitting in individual spectra
- Exclude problematic standards

### Issue 3: Large Intercept

**Symptoms:**
- Intercept >> 0
- Calibration line doesn't pass through origin

**Possible causes:**
- Background contamination
- Systematic bias
- Wrong background subtraction

**Solutions:**
- Check blank measurements
- Verify background subtraction
- Consider forcing zero intercept (advanced)

### Issue 4: Outlier Standard

**Symptoms:**
- One point far from line
- Red cell in statistics table

**Possible causes:**
- Bad spectrum for that standard
- Sample inhomogeneity
- Wrong certified value
- Contamination

**Solutions:**
- Re-measure that standard with multiple spectra
- Check sample quality
- Verify certified concentration
- Exclude standard and recalibrate

## Advanced Features

### Comparing Calibrations

To compare different calibrations:
1. Create calibration with all standards
2. Note R² and errors
3. Uncheck problematic standard
4. Create new calibration
5. Compare R² values and errors

### Validating with Known Samples

After calibration:
1. Measure sample with known concentration
2. Calculate predicted concentration
3. Compare to known value
4. Should match within error bars

### Monitoring Calibration Drift

Over time:
1. Periodically re-measure standards
2. Compare to calibration curve
3. If points drift, recalibrate
4. Document calibration dates

## Best Practices

### 1. Regular Review
- Check calibration plots after each calibration
- Don't skip visual inspection
- Trust your eyes - if it looks wrong, investigate

### 2. Documentation
- Screenshot calibration plots for records
- Note R² values in lab notebook
- Document any excluded standards

### 3. Validation
- Always validate with known samples
- Use independent standards when possible
- Cross-check with other methods

### 4. Recalibration Schedule
- Recalibrate if R² drops
- Recalibrate after instrument maintenance
- Recalibrate if standards change
- Periodic recalibration (monthly/quarterly)

## Technical Details

### Plot Generation

The plot shows:
- **X-axis**: Integrated intensity (cps) from peak fitting
- **Y-axis**: Element concentration (ppm)
- **Line**: y = slope × x + intercept
- **Points**: Back-calculated from certified concentrations

### Intensity Calculation

For plotting, intensities are back-calculated:
```
Given: Concentration = slope × Intensity + intercept
Solve for Intensity: Intensity = (Concentration - intercept) / slope
```

This shows where standards SHOULD plot based on their certified concentrations.

### Color Coding Logic

```python
error_pct = |predicted - certified| / certified × 100

if error_pct < 2%:
    color = green  # Excellent
elif error_pct < 5%:
    color = yellow  # Good
else:
    color = red  # Check this
```

## Keyboard Shortcuts

- **Ctrl+R** (future): Refresh plot
- **Ctrl+S** (future): Save plot image
- **Ctrl+P** (future): Print plot

## Export Options (Future)

Planned features:
- Export plot as PNG/PDF
- Export statistics table as CSV
- Generate calibration report
- Compare multiple calibrations

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Compatible with:** XRF Multi-Element Analysis v2.0+
