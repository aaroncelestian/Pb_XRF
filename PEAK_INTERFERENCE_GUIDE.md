# Peak Interference Correction Guide

## The Problem

**Peak overlap** occurs when two elements have emission lines at nearly the same energy. On portable XRF instruments with limited energy resolution, these peaks are indistinguishable.

### Critical Interference: Pb and As

- **Pb L-alpha**: 10.55 keV
- **As K-alpha**: 10.54 keV
- **Difference**: 0.01 keV (10 eV)

**Typical portable XRF resolution**: ~150-200 eV at 10 keV
**Result**: Cannot distinguish these peaks!

## Current System Warnings

The software now **automatically detects** peak interferences and warns you when:
1. You try to calibrate both Pb and As simultaneously
2. Both elements are selected for analysis in a sample

### Warning Message

```
⚠️ PEAK INTERFERENCE DETECTED ⚠️

The following elements have overlapping emission lines:

• Pb ↔ As
  Pb L-alpha (10.55 keV) and As K-alpha (10.54 keV) are 
  indistinguishable on most portable XRF.

Recommendations:
1. Calibrate elements separately if possible
2. Use standards with only ONE of these elements present
3. Consider using alternative peaks (L-beta, K-beta)
4. Apply interference correction (advanced)
```

## Solutions

### Solution 1: Separate Calibrations (Simplest)

**If you know which element is present:**

**For soil samples (typically high Pb, low As):**
1. Calibrate using Pb standards only
2. Analyze samples assuming all signal is Pb
3. As contribution is negligible

**For environmental samples (variable Pb/As):**
1. Use additional information (sample type, location)
2. If coastal/marine → likely As
3. If urban/industrial → likely Pb

### Solution 2: Use Standards with Only One Element

**Ideal standard set for Pb/As:**

| Standard | Pb (ppm) | As (ppm) | Use for |
|----------|----------|----------|---------|
| NIST 2586 | 432 | N/A | Pb calibration |
| NIST 2587 | 3242 | N/A | Pb calibration |
| Till 1 | 22 | 18 | ⚠️ Has both! |
| LKSD 1 | 82 | 40 | ⚠️ Has both! |

**Problem**: Most environmental standards have BOTH elements!

### Solution 3: Use Alternative Peaks

**For Pb:**
- Primary: L-alpha (10.55 keV) ← Overlaps with As
- **Alternative: L-beta (12.61 keV)** ← No overlap! ✅

**For As:**
- Primary: K-alpha (10.54 keV) ← Overlaps with Pb
- **Alternative: K-beta (11.73 keV)** ← Less overlap ✅

**Trade-offs:**
- ✅ No interference
- ❌ Lower intensity (L-beta and K-beta are weaker)
- ❌ Lower sensitivity
- ❌ Higher detection limits

**To implement** (future feature):
```python
ELEMENT_DEFINITIONS = {
    'Pb': {
        'primary_energy': 12.61,  # Use L-beta instead
        'peak_region': (12.0, 13.2),
        ...
    }
}
```

### Solution 4: Deconvolution (Advanced)

**Mathematical approach** to separate overlapping peaks.

#### Step 1: Measure Pure Element Standards

```
Pure Pb standard (As = 0):
  Measure intensity at 10.55 keV → I_Pb_pure

Pure As standard (Pb = 0):
  Measure intensity at 10.54 keV → I_As_pure
```

#### Step 2: Calculate Sensitivity Factors

```
Sensitivity_Pb = I_Pb_pure / [Pb]_certified
Sensitivity_As = I_As_pure / [As]_certified
```

#### Step 3: Measure Mixed Sample

```
Sample with both Pb and As:
  Measure intensity at ~10.55 keV → I_total
  
I_total = Sensitivity_Pb × [Pb] + Sensitivity_As × [As]
```

#### Step 4: Solve for Concentrations

**If you have TWO measurements** (e.g., at different energies or using different peaks):

```
I_at_10.55 = a₁[Pb] + b₁[As]
I_at_12.61 = a₂[Pb] + b₂[As]

Solve simultaneous equations:
[Pb] = ...
[As] = ...
```

**If you have ONE measurement** (most common):
- Need additional constraint
- Use ratio from similar samples
- Use external information
- Accept higher uncertainty

### Solution 5: Fundamental Parameters (Most Robust)

**Full FP modeling** accounts for:
- All peak overlaps
- Matrix effects
- Absorption/enhancement
- Secondary fluorescence

**Requires:**
- Specialized software (PyMca, XRF-FP)
- Full spectrum analysis
- Complete sample composition
- Significant computational resources

**Not currently implemented** in this software.

## Practical Workflow

### Scenario 1: Soil Samples (Pb-dominated)

**Assumption**: Pb >> As in urban soils

```
1. Calibrate using Pb standards (NIST 2586, 2587)
2. Ignore As in calibration
3. Analyze samples as "Pb only"
4. Report as "Total Pb + As" if As might be present
5. Note in report: "Values may include As contribution"
```

### Scenario 2: Marine Sediments (As-dominated)

**Assumption**: As >> Pb in marine environments

```
1. Calibrate using As standards
2. Ignore Pb in calibration
3. Analyze samples as "As only"
4. Validate with ICP-MS if critical
```

### Scenario 3: Unknown Samples (Both present)

**Most conservative approach:**

```
1. Run analysis twice:
   a. Assuming all signal is Pb → Get "max Pb"
   b. Assuming all signal is As → Get "max As"

2. Report range:
   "Pb: 0 - 500 ppm (if all As)"
   "As: 0 - 50 ppm (if all Pb)"

3. Use additional information:
   - Sample type
   - Geographic location
   - Historical data
   - Correlation with other elements

4. Consider confirmatory analysis (ICP-MS)
```

### Scenario 4: Research/Regulatory (High accuracy needed)

**Use alternative analytical method:**

```
1. XRF for screening
2. ICP-MS for confirmation
3. Use XRF for elements without interferences
4. Use ICP-MS for Pb/As separation
```

## Future Enhancements

### Planned Features:

1. **Automatic deconvolution** using pure element standards
2. **Alternative peak selection** (L-beta, K-beta)
3. **Interference correction factors** from standards
4. **Multi-peak fitting** for partial separation
5. **Integration with external data** (ICP-MS results)

### Advanced Options (Future):

```python
# Option to use alternative peaks
use_alternative_peaks = True

# Deconvolution settings
apply_interference_correction = True
interference_standards = {
    'Pb_pure': 'NIST_2586.txt',  # Pure Pb, no As
    'As_pure': 'Custom_As_std.txt'  # Pure As, no Pb
}

# Constraint-based solving
constraints = {
    'Pb': {'min': 0, 'max': 5000},  # ppm
    'As': {'min': 0, 'max': 100}
}
```

## Best Practices

### 1. Know Your Samples

- **Urban soil**: Likely Pb-dominated
- **Marine sediment**: Likely As-dominated
- **Mine tailings**: Could be either
- **Industrial sites**: Check history

### 2. Use Complementary Information

- Geographic location
- Sample appearance
- Historical data
- Correlation with other elements (e.g., Pb often with Zn)

### 3. Validate Critical Results

- Use ICP-MS for regulatory samples
- Cross-check with alternative methods
- Analyze certified reference materials
- Compare with literature values

### 4. Report Honestly

**Good reporting:**
```
"Pb: 450 ± 50 ppm (may include As contribution due to peak overlap)"
"Pb+As (combined): 450 ± 50 ppm"
"Pb: 450 ppm (assuming As < 10 ppm)"
```

**Bad reporting:**
```
"Pb: 450 ppm" (without mentioning potential As interference)
```

### 5. Document Assumptions

Always note:
- Which peaks were used
- Whether interference correction was applied
- Assumptions made about sample composition
- Validation performed

## Summary

**Current capabilities:**
- ✅ Automatic interference detection
- ✅ Warnings when Pb and As both selected
- ✅ Guidance on best practices

**Recommended approach:**
1. Use separate calibrations when possible
2. Know your sample type
3. Report conservatively
4. Validate critical results

**Future capabilities:**
- Deconvolution algorithms
- Alternative peak selection
- Interference correction factors
- Multi-peak fitting

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Compatible with:** XRF Multi-Element Analysis v2.0+
