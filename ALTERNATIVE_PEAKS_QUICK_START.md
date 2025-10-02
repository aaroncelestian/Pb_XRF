# Alternative Peaks Quick Start Guide

## Problem: Pb and As Overlap

**Pb L-alpha (10.55 keV)** and **As K-alpha (10.54 keV)** are indistinguishable on portable XRF.

## Solution: Use Alternative Peaks

### Quick Setup (2 minutes)

#### For Lead (Pb):
1. **Calibrations tab** → Select "Pb"
2. **Peak to Use:** Select "Alternative"
3. ✅ Now using **Pb L-beta (12.61 keV)** - no As interference!

#### For Arsenic (As):
1. **Calibrations tab** → Select "As"
2. **Peak to Use:** Select "Alternative"
3. ✅ Now using **As K-beta (11.73 keV)** - no Pb interference!

## When to Use

### Use Alternative Peaks ✅
- Both Pb AND As present in samples
- Need accurate separation
- Concentrations > 50 ppm (well above detection limits)
- High-quality spectra available

### Use Primary Peaks ✅
- Only Pb OR As present (not both)
- Near detection limits (need max sensitivity)
- Known sample type (e.g., urban soil = mostly Pb)

## Trade-offs

| Aspect | Primary Peaks | Alternative Peaks |
|--------|--------------|-------------------|
| **Interference** | ❌ Overlap | ✅ No overlap |
| **Sensitivity** | ✅ High | ⚠️ Lower (2-3x) |
| **Detection Limit** | ✅ ~50 ppm | ⚠️ ~100-150 ppm |
| **Accuracy** | ⚠️ If both present | ✅ Independent |

## Complete Workflow

### Step 1: Calibrate Pb (L-beta)
```
1. Calibrations tab
2. Element: Pb
3. Peak: Alternative (L-beta)
4. Click "🤖 Auto Current" or "🚀 Auto ALL"
5. Select Pb standards (NIST 2586, 2587)
6. Calibration uses L-beta peak ✅
```

### Step 2: Calibrate As (K-beta)
```
1. Element: As
2. Peak: Alternative (K-beta)
3. Click "🤖 Auto Current"
4. Select As standards
5. Calibration uses K-beta peak ✅
```

### Step 3: Analyze Samples
```
1. Main Workflow tab
2. Select elements: ☑️ Pb, ☑️ As
3. Process samples
4. Both measured independently! ✅
```

## Peak Energies Reference

### Lead (Pb)
- **Primary:** L-alpha = 10.55 keV (overlaps As)
- **Alternative:** L-beta = 12.61 keV ✅

### Arsenic (As)
- **Primary:** K-alpha = 10.54 keV (overlaps Pb)
- **Alternative:** K-beta = 11.73 keV ✅

### No Overlap!
```
Energy scale (keV):
10.0    10.5    11.0    11.5    12.0    12.5    13.0
 |       |       |       |       |       |       |
         Pb-Lα
         As-Kα   
         (OVERLAP!)
                         As-Kβ
                                         Pb-Lβ
                                         (SEPARATED!)
```

## Visual Guide

### In the UI:

**Element & Peak Selection:**
```
Current Element: [Pb ▼]
Peak to Use: [Alternative ▼]
ℹ️ Alternative: L-beta at 12.61 keV - Use to avoid As K-alpha interference (lower intensity)
```

**Element Properties (updates automatically):**
```
Primary Energy (keV): 12.61 (L-beta)
Peak Region (keV): 12.0 - 13.2
Integration Region (keV): 11.8 - 13.4
```

## Troubleshooting

### Q: Dropdown is disabled?
**A:** Element doesn't have alternative peak. Only Pb and As have alternatives currently.

### Q: Lower concentrations than expected?
**A:** Alternative peaks are less intense. This is normal. Calibrate with alternative peak and it will be accurate.

### Q: Can I switch back to primary?
**A:** Yes! Just select "Primary (default)" from dropdown.

### Q: Do I need to recalibrate?
**A:** Yes. Primary and alternative peaks need separate calibrations.

### Q: Which peak for mixed Pb/As samples?
**A:** Use alternative peaks for both elements to avoid interference.

## Best Practices

### 1. Calibration Strategy
- **If analyzing Pb only:** Use primary (L-alpha) for best sensitivity
- **If analyzing As only:** Use primary (K-alpha) for best sensitivity
- **If analyzing both:** Use alternative peaks for both ✅

### 2. Detection Limits
- **Primary peaks:** Pb ~50 ppm, As ~20 ppm
- **Alternative peaks:** Pb ~100 ppm, As ~50 ppm
- Plan accordingly!

### 3. Quality Control
- Run standards with both peak selections
- Compare results
- Document which peak was used
- Note in reports: "Pb measured using L-beta to avoid As interference"

### 4. Sample Requirements
For alternative peaks to work well:
- Good counting statistics (longer measurement time)
- Clean spectra (low background)
- Concentrations well above detection limits

## Summary

**Alternative peaks solve the Pb/As interference problem!**

✅ **Pros:**
- No interference
- Independent measurements
- Accurate for both elements

⚠️ **Cons:**
- Lower sensitivity
- Higher detection limits
- Need good quality spectra

**Bottom line:** Use alternative peaks when both Pb and As are present and concentrations are sufficient. Use primary peaks for maximum sensitivity when only one element is present.

---

**Quick Reference:**
- Pb primary: 10.55 keV (L-alpha) → Pb alternative: 12.61 keV (L-beta)
- As primary: 10.54 keV (K-alpha) → As alternative: 11.73 keV (K-beta)

**Access:** Calibrations tab → Peak to Use dropdown
