# Calibration Plot Visualization Guide

## New Feature: Individual Measurement Display

The calibration plots now show **ALL individual measurements** from your multi-spectra averaging, not just the averaged points!

## What You'll See

### Plot Elements

**1. Light coral dots (small)** 🔴
- Individual measurements from each spectrum
- Shows the spread/variability in your data
- Multiple dots at same concentration = multiple spectra for that standard

**2. Dark red circles (large)** 🔴
- Averaged values used for calibration
- One point per standard
- These are the points the calibration line is fit to

**3. Blue line** 🔵
- Calibration curve
- Fit through the averaged points
- Equation shown in legend

### Example Visualization

```
Fe Calibration Curve
R² = 0.915

Y-axis: Concentration (ppm)
X-axis: Intensity (cps)

At LKSD 1 (28090 ppm):
  • 5 light coral dots (individual measurements)
  • 1 dark red circle (average)
  • Dots show spread around average

At NIST 2586 (5760 ppm):
  • 3 light coral dots
  • 1 dark red circle
  • Tighter clustering = better precision
```

## Interpreting the Spread

### Good Data Quality ✅

**Tight clustering:**
```
Standard A at 1000 ppm:
  ○ ○ ○  ← All measurements close together
    ●    ← Average
```

**Indicates:**
- Good measurement precision
- Homogeneous sample
- Stable instrument
- Low RSD (<2%)

### Moderate Variability ⚠️

**Some spread:**
```
Standard B at 2000 ppm:
  ○   ○ ○   ← Some scatter
      ●      ← Average
```

**Indicates:**
- Acceptable precision
- RSD 2-5%
- Normal for lower concentrations

### Poor Data Quality ❌

**Wide scatter:**
```
Standard C at 500 ppm:
  ○     ○       ○  ← Large spread
        ●           ← Average uncertain
```

**Indicates:**
- Poor precision (RSD >10%)
- Possible issues:
  - Inhomogeneous sample
  - Near detection limit
  - Instrumental drift
  - Positioning errors

## Benefits of Seeing Individual Points

### 1. Quality Assessment
- **Visual check** of measurement precision
- Identify problematic standards immediately
- See if one measurement is an outlier

### 2. Outlier Detection
```
Standard with outlier:
  ○ ○ ○         ○  ← One point far from others
      ●             ← Average pulled by outlier
```

**Action:** Consider excluding that spectrum and recalibrating

### 3. Confidence in Calibration
- **Tight clusters** → High confidence
- **Wide scatter** → Lower confidence
- Helps decide if you need more measurements

### 4. Troubleshooting
- See which standards have high variability
- Identify systematic issues
- Guide decisions about re-measurement

## Example Scenarios

### Scenario 1: Excellent Calibration

**What you see:**
- All individual points cluster tightly around averages
- Points lie close to calibration line
- R² > 0.99

**Interpretation:**
✅ High-quality data
✅ Reliable calibration
✅ Ready to use

### Scenario 2: One Problematic Standard

**What you see:**
- 3 standards have tight clusters
- 1 standard has wide scatter
- R² = 0.96 (decent but not great)

**Interpretation:**
⚠️ One standard has issues
**Action:**
- Re-measure that standard
- Or exclude it and recalibrate with 3 standards

### Scenario 3: Systematic Bias

**What you see:**
- All points cluster tightly (good precision)
- But all points systematically above or below line
- R² is good but predictions are off

**Interpretation:**
❌ Systematic error
**Possible causes:**
- Wrong certified concentrations
- Matrix effects
- Incorrect peak regions

### Scenario 4: Near Detection Limit

**What you see:**
- Low-concentration standards have wide scatter
- High-concentration standards have tight clusters
- Funnel shape in the scatter

**Interpretation:**
⚠️ Normal behavior near detection limit
**Action:**
- Accept higher uncertainty at low concentrations
- Consider excluding lowest standard
- Report detection limit honestly

## Visual Quality Indicators

### Tight Horizontal Spread (Good)
```
Concentration
    ^
    |     ○○○●○○  ← Tight cluster
    |
    +-----------> Intensity
```
**RSD < 2%** - Excellent precision

### Wide Horizontal Spread (Poor)
```
Concentration
    ^
    |   ○  ○●○  ○  ← Wide scatter
    |
    +-----------> Intensity
```
**RSD > 5%** - Check data quality

### Points Near Line (Good Calibration)
```
Concentration
    ^
    |        ●  ← All points
    |      ●     near line
    |    ●
    |  ●  ────── Calibration line
    +-----------> Intensity
```
**R² > 0.99** - Excellent fit

### Points Scattered Around Line (Poor)
```
Concentration
    ^
    |    ●
    |  ●   ●  ← Points scattered
    |      ●  ────── Line doesn't fit well
    +-----------> Intensity
```
**R² < 0.95** - Poor fit, recalibrate

## Using This Information

### Before Accepting Calibration:

1. **Check individual point spread**
   - Tight clusters? ✅ Good
   - Wide scatter? ⚠️ Investigate

2. **Check points vs. line**
   - Close to line? ✅ Good fit
   - Systematic deviation? ❌ Problem

3. **Check R² value**
   - R² > 0.99? ✅ Excellent
   - R² < 0.95? ❌ Recalibrate

4. **Check for outliers**
   - One point far from cluster? ⚠️ Exclude and remeasure

### During Troubleshooting:

**If calibration looks poor:**

1. **Look at individual points**
   - Which standard has high scatter?
   - Are there outliers?

2. **Check the statistics table**
   - Which standards have red cells?
   - Do predicted values match certified?

3. **Review progress log**
   - What were the RSD values?
   - Were there any error messages?

4. **Take action**
   - Re-measure problematic standards
   - Exclude bad data
   - Add more standards

## Legend Guide

**In the plot legend:**
- **Blue line**: "Calibration: y = [slope]x + [intercept]"
- **Light coral dots**: "Individual measurements"
- **Dark red circles**: "Averaged standards"

**Visual hierarchy:**
1. Individual measurements (background layer)
2. Calibration line (middle layer)
3. Averaged points (foreground layer)

## Technical Details

### Data Storage

Calibration now stores:
```json
{
  "Fe": {
    "slope": 2.1834,
    "intercept": -15236.93,
    "r_squared": 0.915,
    "standards_used": ["LKSD 1", "NIST 2586", "NIST 2587", "PACS 2"],
    "raw_intensities": {
      "LKSD 1": [2041.1, 2043.5, 2039.8, 2042.2, 2040.9],
      "NIST 2586": [3156.6, 3158.1, 3155.2],
      "NIST 2587": [2047.2, 2048.8],
      "PACS 2": [719.5, 720.1, 718.9, 721.2]
    }
  }
}
```

### Plotting Logic

```python
# For each standard:
for standard in standards_used:
    raw_measurements = raw_intensities[standard]
    certified_conc = get_certified_concentration(standard)
    
    # Plot individual measurements
    plot_scatter(raw_measurements, [certified_conc] * len(raw_measurements))
    
    # Plot average
    avg_intensity = mean(raw_measurements)
    plot_scatter([avg_intensity], [certified_conc], larger_size)
```

## Comparison: Before vs. After

### Before (Single Points)
```
Plot shows:
  ● ● ● ●  ← 4 standards, no error information
```

**Problem:** Can't see measurement variability

### After (Individual + Averaged)
```
Plot shows:
  ○○○●○○  ○○●○  ○●○  ●  ← All measurements visible
```

**Benefit:** See precision and spread for each standard!

## Best Practices

### 1. Visual Inspection First
- Always look at the plot before accepting calibration
- Trust your eyes - if it looks wrong, investigate

### 2. Check for Patterns
- Funnel shape? → Detection limit issues
- Systematic offset? → Bias or matrix effects
- Random scatter? → Poor measurement quality

### 3. Use with Statistics
- Combine visual inspection with RSD values
- Cross-reference with statistics table
- Both should tell the same story

### 4. Document Issues
- Screenshot plots with problems
- Note which standards were excluded
- Keep records for troubleshooting

## Summary

**New visualization shows:**
- ✅ All individual measurements (light coral dots)
- ✅ Averaged points (dark red circles)
- ✅ Calibration line (blue)
- ✅ Visual assessment of data quality
- ✅ Easy identification of outliers
- ✅ Confidence in calibration

**You can now:**
- See measurement spread at a glance
- Identify problematic standards visually
- Assess calibration quality comprehensively
- Make informed decisions about data quality

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Note:** Individual measurements only shown if multi-spectra averaging was used during calibration
