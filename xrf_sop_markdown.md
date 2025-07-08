# Standard Operating Procedure: XRF Analysis of Lead (Pb) in Pressed Pellets

**Document ID:** SOP-XRF-Pb-001  
**Version:** 1.0  
**Effective Date:** [Insert Date]  
**Review Date:** [Annual Review]  
**Approved By:** [Insert Name/Title]

---

## 1. Purpose and Scope

This Standard Operating Procedure (SOP) describes the quantitative analysis of lead (Pb) in solid samples using X-ray fluorescence (XRF) spectroscopy with Si detector systems. The method employs pressed pellet sample preparation and Gaussian-A peak fitting for accurate quantification of Pb L-alpha emissions at 10.5 keV.

**Applicable Sample Types:** Solid materials suitable for grinding and pellet pressing  
**Detection Range:** 10 ppm to 10,000+ ppm Pb  
**Precision:** <5% RSD (typically 2-3% RSD)  
**Accuracy:** ±5% (with proper calibration)

---

## 2. Safety Considerations

- **Lead Exposure:** Follow appropriate safety protocols when handling Pb-containing samples
- **Sample Preparation:** Use appropriate PPE during grinding and pressing operations
- **X-ray Safety:** Ensure XRF instrument safety interlocks are functional
- **Chemical Safety:** Handle binder materials according to MSDS recommendations

---

## 3. Equipment and Materials

### 3.1 Instrumentation
- XRF spectrometer with Si detector
- X-ray tube capable of 50 kV operation
- Sample positioning system with 1.2 mm beam collimation
- Dead time monitoring capability

### 3.2 Sample Preparation Equipment
- Sample grinder (target: <75 μm particle size)
- Analytical balance (±0.001 g precision)
- Pellet press capable of 5 tons pressure
- 15 mm diameter pressing die
- Mixing equipment

### 3.3 Materials
- Binding agent (e.g., wax, cellulose, or appropriate binder)
- Cleaning solvents for die maintenance
- Certified Reference Materials (CRMs) for calibration
- NIST standards for Pb quantification

---

## 4. Sample Preparation Protocol

### 4.1 Sample Grinding
1. **Grinding Procedure:**
   - Grind sample to uniform particle size (<75 μm)
   - Ensure complete homogenization
   - Avoid contamination between samples
   - Document grinding time and conditions

2. **Quality Check:**
   - Verify particle size distribution if critical
   - Ensure no visible heterogeneity

### 4.2 Sample Weighing
1. **Precise Weighing:**
   - Weigh **2.000 ± 0.001 g** of ground sample
   - Weigh **0.400 ± 0.001 g** of binder
   - Record all masses in laboratory notebook
   - Calculate dilution factor: 2.0/(2.0+0.4) = 0.833

2. **Documentation:**
   - Sample ID and description
   - Preparation date and analyst
   - Actual masses (not target masses)

### 4.3 Mixing and Homogenization
1. **Mixing Protocol:**
   - Combine sample and binder in mixing container
   - Mix thoroughly for **2 minutes minimum**
   - Ensure uniform distribution
   - Avoid static buildup

### 4.4 Pellet Pressing
1. **Die Preparation:**
   - Clean 15 mm die with appropriate solvent
   - Ensure die is completely dry
   - Check for damage or wear

2. **Pressing Procedure:**
   - Transfer mixture to 15 mm die
   - Distribute evenly in die cavity
   - Apply **5 tons pressure** for **5 minutes**
   - Maintain consistent pressure throughout pressing time

3. **Pellet Quality Assessment:**
   - Remove pellet carefully from die
   - Inspect for cracks, chips, or other defects
   - Weigh pellet (target: **2.40 ± 0.05 g**)
   - Record pellet thickness if measured
   - Reject pellets with visible defects

---

## 5. XRF Instrument Setup

### 5.1 Instrumental Parameters
| Parameter | Setting | Notes |
|-----------|---------|-------|
| **Tube Voltage** | 50 kV | Fixed parameter |
| **Tube Current** | Auto | Optimize for dead time |
| **Beam Size** | 1.2 mm | Fixed collimation |
| **Filters** | None | No filters used |
| **Detector** | Si detector | Energy resolution <150 eV |
| **Measurement Time** | 30 seconds | Live time, not real time |
| **Target Dead Time** | 20% ± 5% | Optimal range: 15-25% |

### 5.2 Dead Time Optimization
1. **Initial Setup:**
   - Position pellet in sample holder
   - Ensure 1.2 mm beam hits sample surface
   - Start with moderate tube current

2. **Current Optimization:**
   - Adjust tube current to achieve 15-25% dead time
   - Monitor count rate stability
   - Record final current and dead time settings
   - **Critical:** Dead time must be within 15-25% range

### 5.3 Quality Checks
- Verify beam alignment using positioning standards
- Check energy calibration with known peaks
- Confirm detector resolution meets specifications
- Monitor tube stability throughout session

---

## 6. Measurement Protocol

### 6.1 Sample Positioning
1. **Positioning Procedure:**
   - Place pellet in sample holder with smooth surface facing detector
   - Ensure pellet is flat and secure
   - Verify beam hits pellet center (avoid edges)
   - Check that measurement area is representative

### 6.2 Measurement Sequence
1. **Individual Measurements:**
   - Measure each pellet for **30 seconds** (live time)
   - Record dead time percentage for each measurement
   - Collect **minimum 6 replicate measurements** per sample
   - Monitor count rate stability during measurements

2. **Data Quality Criteria:**
   - Dead time: 15-25% for each measurement
   - Count rate stability: <5% variation during measurement
   - Spectral quality: Clear Pb L-alpha peak at 10.5 keV

### 6.3 Quality Control Measurements
1. **Reference Materials:**
   - Analyze certified reference material every **10 samples**
   - Use matrix-matched CRMs when available
   - Document CRM results and compare to certified values

2. **Blank Analysis:**
   - Analyze blank pellet (binder only) **daily**
   - Monitor blank levels for contamination
   - Establish control limits for blank measurements

3. **Duplicate Analysis:**
   - Prepare and analyze duplicate pellets from same sample
   - Target: <5% RSD between duplicates
   - Investigate if precision exceeds limits

---

## 7. Data Analysis Protocol

### 7.1 Spectral Processing
1. **Peak Integration:**
   - Apply Gaussian-A fitting to Pb L-alpha peak
   - Integration region: 9.8 - 11.2 keV (typical)
   - Background subtraction: Linear baseline
   - Calculate integrated intensity (background-corrected)

2. **Interference Check:**
   - Verify no spectral interferences near 10.5 keV
   - Check for As K-alpha overlap (10.54 keV)
   - Document any unusual spectral features

### 7.2 Calibration Application
1. **NIST Calibration Curve:**
   - Apply calibration: **Concentration = 13.8913 × Intensity + 0**
   - This gives concentration in pellet
   - Correct for dilution: **Original Concentration = Pellet Conc ÷ 0.833**

2. **Statistical Analysis:**
   - Calculate mean integrated intensity from replicates
   - Calculate standard deviation and RSD
   - Apply calibration to mean intensity
   - Propagate uncertainties through calculations

### 7.3 Uncertainty Assessment
**Typical Uncertainty Budget:**
- Sample weighing: ±0.05%
- Binder weighing: ±0.25%
- XRF precision: ±2.0%
- Calibration: ±3.0%
- **Total combined uncertainty: ±3.7%** (k=1)

---

## 8. Quality Control and Acceptance Criteria

### 8.1 Precision Criteria
| Parameter | Acceptance Limit | Action if Exceeded |
|-----------|------------------|-------------------|
| **Sample RSD** | <5% | Investigate sample homogeneity |
| **Duplicate RSD** | <5% | Repeat sample preparation |
| **CRM Recovery** | 95-105% | Check calibration |
| **Dead Time** | 15-25% | Adjust tube current |

### 8.2 Control Charts
- Maintain control charts for:
  - CRM recovery over time
  - Blank levels
  - Measurement precision
  - Dead time stability

### 8.3 Corrective Actions
| Issue | Probable Cause | Corrective Action |
|-------|----------------|-------------------|
| High RSD (>5%) | Sample inhomogeneity | Re-grind and re-prepare |
| Low dead time (<15%) | Low tube current | Increase current or check positioning |
| High dead time (>25%) | High tube current | Decrease current |
| Poor CRM recovery | Calibration drift | Re-calibrate with standards |
| Spectral interference | Sample composition | Verify peak identification |

---

## 9. Results Reporting

### 9.1 Required Information
**For each sample, report:**
- Sample identification
- Number of replicate measurements
- Mean Pb concentration ± standard deviation
- Relative standard deviation (RSD)
- Measurement conditions (dead time, count time)
- Date of analysis and analyst

### 9.2 Detection Limits
- **Limit of Detection (LOD):** Calculate from blank measurements
- **Limit of Quantification (LOQ):** Report as 3.3 × LOD
- **Typical LOD:** 5-10 ppm Pb (depends on matrix)

### 9.3 Uncertainty Statement
- Report expanded uncertainty (k=2, ~95% confidence)
- Include all significant uncertainty sources
- Typical expanded uncertainty: ±7-10%

---

## 10. Maintenance and Troubleshooting

### 10.1 Routine Maintenance
**Daily:**
- Check dead time optimization
- Analyze blank pellet
- Verify beam alignment

**Weekly:**
- Clean sample chamber
- Check calibration with CRM
- Inspect pressing die condition

**Monthly:**
- Energy calibration verification
- Detector resolution check
- Complete system performance verification

### 10.2 Common Issues and Solutions

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **Poor precision** | High RSD (>5%) | Check sample prep, verify dead time |
| **Calibration drift** | CRM recovery outside limits | Re-calibrate with fresh standards |
| **Low count rates** | Dead time <15% | Increase tube current, check sample |
| **Spectral artifacts** | Unusual peak shapes | Check detector resolution, energy cal |
| **Pellet defects** | Cracks or chips | Re-press pellet, check die condition |

---

## 11. Documentation and Records

### 11.1 Required Records
- Laboratory notebook with all measurements
- Calibration certificates and verification data
- Control chart data and trend analysis
- Maintenance records and corrective actions
- Sample preparation worksheets

### 11.2 Data Retention
- Raw spectral data: 5 years minimum
- Calibration records: Life of calibration + 2 years
- Quality control data: 3 years minimum
- Method validation data: Permanent

---

## 12. Method Validation Summary

This method has been validated for:
- **Accuracy:** Verified against NIST SRMs
- **Precision:** <5% RSD demonstrated
- **Linearity:** R² >0.999 over working range
- **Detection limits:** Appropriate for intended use
- **Robustness:** Stable under normal operating conditions

**Last Validation Date:** [Insert Date]  
**Next Review Date:** [Annual]

---

## 13. References and Standards

1. ASTM E1621 - Standard Guide for Elemental Analysis by Wavelength Dispersive X-Ray Fluorescence Spectrometry
2. ISO 12677 - Chemical analysis of refractory products by X-ray fluorescence
3. NIST SRM certificates for calibration standards
4. Internal method validation studies

---

**Document Control:**
- Original Author: [Name]
- Technical Review: [Name/Date]
- Quality Assurance Review: [Name/Date]
- Management Approval: [Name/Date]

---

*This SOP should be reviewed annually and updated as needed to reflect current best practices and regulatory requirements.*