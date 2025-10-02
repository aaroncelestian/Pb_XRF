# Custom Standards & Selective Calibration Guide

## Overview

The Multi-Element Calibration system now supports:
1. **Selective Standard Usage** - Choose which reference materials to include in calibration
2. **Custom Standards** - Add your own standards with user-defined concentrations
3. **Flexible Element Selection** - Specify which elements are present in each custom standard

## Features

### 1. Standard Selection Checkboxes

Each reference material in the calibration dialog now has a checkbox in the "Use" column:
- ✅ **Checked** = Standard will be included in calibration
- ⬜ **Unchecked** = Standard will be excluded from calibration

**Benefits:**
- Use only the standards you have available
- Exclude problematic standards with poor quality spectra
- Create calibrations with different standard combinations for comparison
- Minimum 2 standards required for calibration (for linear regression)

### 2. Add Custom Standards

Click the **"➕ Add Custom Standard"** button to add your own reference materials.

#### Custom Standard Dialog

**Standard Name:**
- Enter a descriptive name (e.g., "Lab Standard A", "Soil Sample 123")
- Will appear in the standards table marked as "(Custom)"
- Highlighted in light blue to distinguish from built-in standards

**Element Concentrations:**
| Include | Element | Concentration (ppm) |
|---------|---------|---------------------|
| ☑️      | Pb (Lead) | 1500 |
| ☑️      | Zn (Zinc) | 850 |
| ⬜      | Cu (Copper) | - |

- **Include checkbox**: Select which elements are present in your standard
- **Concentration field**: Enter the certified/known concentration in ppm
- Can include any combination of the 10 supported elements

### 3. How It Works

#### Workflow:
1. **Open Calibration Dialog**
   - Advanced Parameters → Multi-Element Calibrations
   - Click "🧮 Create Calibration from Standards"

2. **Select Built-in Standards** (Optional)
   - Check/uncheck boxes for NIST, Till, LKSD, PACS, etc.
   - Only checked standards will be used

3. **Add Custom Standards** (Optional)
   - Click "➕ Add Custom Standard"
   - Enter standard name
   - Check elements present in your standard
   - Enter concentrations for each element
   - Click "Add Standard"
   - Repeat for multiple custom standards

4. **Select Spectra Files**
   - For each standard (built-in or custom), click "Select File..."
   - Choose the XRF spectrum file for that standard

5. **Run Calibration**
   - Click "🚀 Analyze Selected Standards & Create Calibrations"
   - System analyzes only the checked standards
   - Creates calibration curves for each element

## Example Use Cases

### Case 1: Limited Standards Available
You only have 3 NIST standards:
- ✅ Check: NIST 2586, NIST 2587, NBS 1633
- ⬜ Uncheck: All others
- Result: Calibration uses only your 3 available standards

### Case 2: Custom Lab Standards
You have in-house standards with known concentrations:
1. Add Custom Standard: "Lab Std 1"
   - Pb: 500 ppm
   - Zn: 300 ppm
   - Cu: 150 ppm

2. Add Custom Standard: "Lab Std 2"
   - Pb: 2000 ppm
   - Zn: 1200 ppm
   - Cu: 800 ppm

3. Combine with 1-2 NIST standards for validation

### Case 3: Element-Specific Calibration
Creating a Lead-only calibration:
- Use standards that have good Pb values
- Uncheck standards with uncertain Pb concentrations
- Custom standards can have just Pb specified

### Case 4: Quality Control
Exclude problematic standards:
- Uncheck standards with poor spectral quality
- Uncheck standards with damaged/contaminated samples
- Keep only high-quality reference materials

## Technical Details

### Custom Standard Data Storage
- Custom standards are stored in `self.custom_standards_data` dictionary
- Format: `{standard_name: {element_symbol: concentration}}`
- Example:
  ```python
  {
    "Lab Std 1": {
      "Pb": 500.0,
      "Zn": 300.0,
      "Cu": 150.0
    }
  }
  ```

### Concentration Units
- **All concentrations in ppm** (parts per million)
- For % values: multiply by 10,000 to convert to ppm
  - Example: 1.5% = 15,000 ppm

### Peak Integration
- Custom standards use the same peak regions as built-in standards
- Peak regions defined in `ELEMENT_DEFINITIONS` for each element
- Automatic background subtraction applied
- Gaussian fitting for accurate peak integration

### Calibration Requirements
- **Minimum 2 standards** required per element for linear regression
- More standards = better calibration quality
- R² value calculated for calibration quality assessment
- Standards can be any combination of built-in and custom

## Best Practices

### 1. Standard Selection
- Use at least 3-4 standards when possible for robust calibration
- Include standards spanning your expected concentration range
- Mix high and low concentration standards

### 2. Custom Standard Concentrations
- Use certified values when available
- Document source of concentration values
- Consider measurement uncertainty
- Verify concentrations with independent methods when possible

### 3. Quality Assurance
- Always check R² values (aim for > 0.99)
- Review calibration plots for outliers
- Validate with known samples
- Re-run calibration if standards change

### 4. File Organization
- Name spectrum files clearly (e.g., "NIST_2586_run1.txt")
- Keep standards organized in dedicated folder
- Document which file corresponds to which standard
- Save calibration results for future reference

## Troubleshooting

### "No Standards Selected"
- At least one standard must be checked
- Check the "Use" column checkboxes

### "Missing Files"
- All checked standards must have a spectrum file selected
- Uncheck standards you don't have files for, or add the files

### "Invalid Concentration"
- Concentrations must be numeric values
- Use ppm units (not %)
- Don't use special characters or text

### "No Elements"
- At least one element must be checked in custom standard
- Enter concentration value for each checked element

## Future Enhancements

Potential additions:
- Save/load custom standard libraries
- Import standards from CSV files
- Uncertainty propagation for custom standards
- Multi-file averaging for custom standards
- Standard validation tools

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Compatible with:** XRF Multi-Element Analysis v2.0+
