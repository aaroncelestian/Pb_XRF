# Enhanced XRF analysis accounting for pellet preparation protocol

import numpy as np
import pandas as pd

class PelletBasedXRFAnalysis:
    """
    XRF analysis optimized for pressed pellet samples with standardized preparation
    """
    
    def __init__(self):
        # Pellet preparation parameters
        self.sample_mass = 2.0  # grams
        self.binder_mass = 0.4  # grams
        self.total_mass = self.sample_mass + self.binder_mass
        self.dilution_factor = self.sample_mass / self.total_mass  # 0.833
        
        # Pellet physical parameters
        self.pellet_diameter = 15.0  # mm
        self.pellet_area = np.pi * (self.pellet_diameter/2)**2  # mm²
        self.press_pressure = 5.0  # tons
        self.press_time = 5.0  # minutes
        
        # NIST calibration (adjusted for dilution if needed)
        self.calibration_slope = 13.8913
        self.calibration_intercept = 0.0
        
    def calculate_concentration_in_original_sample(self, measured_concentration):
        """
        Convert pellet concentration back to original sample concentration
        accounting for binder dilution
        """
        # If calibration was done on pellets, concentration is already corrected
        # If calibration was done on pure materials, need to correct for dilution
        original_concentration = measured_concentration / self.dilution_factor
        return original_concentration
    
    def pellet_quality_assessment(self, pellet_mass, pellet_thickness=None):
        """
        Assess pellet quality based on mass and thickness measurements
        
        Parameters:
        - pellet_mass: measured mass of pressed pellet (should be ~2.4g)
        - pellet_thickness: measured thickness (optional)
        
        Returns:
        - quality_flags: list of potential issues
        - density: calculated pellet density
        """
        quality_flags = []
        
        # Check mass consistency
        expected_mass = self.total_mass
        mass_deviation = abs(pellet_mass - expected_mass) / expected_mass * 100
        
        if mass_deviation > 2.0:  # >2% deviation
            quality_flags.append(f"Mass deviation: {mass_deviation:.1f}% (target: ±2%)")
        
        # Check density if thickness provided
        density = None
        if pellet_thickness is not None:
            pellet_volume = self.pellet_area * pellet_thickness  # mm³
            density = pellet_mass / (pellet_volume / 1000)  # g/cm³
            
            # Typical pressed pellet density should be 1.5-3.0 g/cm³
            if density < 1.5 or density > 3.5:
                quality_flags.append(f"Unusual density: {density:.2f} g/cm³ (expected: 1.5-3.0)")
        
        return quality_flags, density
    
    def protocol_validation_checklist(self):
        """
        Generate a validation checklist for the pellet preparation protocol
        """
        checklist = {
            "Sample Preparation": [
                "Samples ground to uniform particle size (<75 μm recommended)",
                "Sample mass measured to ±0.001g precision",
                "Binder mass measured to ±0.001g precision", 
                "Homogeneous mixing of sample and binder",
                "No contamination during preparation"
            ],
            "Pellet Pressing": [
                "Press pressure calibrated and consistent (5 tons)",
                "Press time standardized (5 minutes)",
                "Die cleaned between samples",
                "Pellet diameter consistent (15mm ±0.1mm)",
                "Pellet surface smooth and crack-free"
            ],
            "Quality Control": [
                "Pellet mass within ±2% of target (2.4g)",
                "Regular analysis of reference materials",
                "Blank pellets (binder only) analyzed",
                "Duplicate pellets from same sample show <5% RSD",
                "Visual inspection for cracks or inhomogeneity"
            ],
            "XRF Measurement": [
                "Consistent sample positioning in spectrometer",
                "Stable excitation conditions",
                "Appropriate measurement time for precision",
                "Background/drift corrections applied",
                "Spectral interference check performed"
            ]
        }
        return checklist
    
    def estimate_uncertainty_budget(self, 
                                  weighing_precision=0.001,  # g
                                  xrf_precision_rsd=2.0,     # %
                                  calibration_uncertainty=3.0,  # %
                                  pellet_homogeneity_rsd=1.5):  # %
        """
        Estimate total measurement uncertainty from all sources
        
        This follows ISO/GUM principles for uncertainty propagation
        """
        # Convert precision values to relative uncertainties
        sample_weighing_rel = weighing_precision / self.sample_mass * 100  # %
        binder_weighing_rel = weighing_precision / self.binder_mass * 100  # %
        
        # Dilution factor uncertainty (from weighing)
        dilution_uncertainty = np.sqrt(sample_weighing_rel**2 + binder_weighing_rel**2)
        
        # Combined relative standard uncertainty
        total_relative_uncertainty = np.sqrt(
            xrf_precision_rsd**2 +
            calibration_uncertainty**2 +
            pellet_homogeneity_rsd**2 +
            dilution_uncertainty**2
        )
        
        uncertainty_budget = {
            'sample_weighing_uncertainty_%': sample_weighing_rel,
            'binder_weighing_uncertainty_%': binder_weighing_rel,
            'dilution_factor_uncertainty_%': dilution_uncertainty,
            'xrf_precision_uncertainty_%': xrf_precision_rsd,
            'calibration_uncertainty_%': calibration_uncertainty,
            'pellet_homogeneity_uncertainty_%': pellet_homogeneity_rsd,
            'total_relative_uncertainty_%': total_relative_uncertainty,
            'coverage_factor_k=2': 2 * total_relative_uncertainty  # ~95% confidence
        }
        
        return uncertainty_budget
    
    def optimize_measurement_conditions(self, target_precision_rsd=2.0, target_dead_time=20.0):
        """
        Calculate optimal measurement parameters for Si detector XRF
        
        Based on Poisson counting statistics: RSD ≈ 1/√(total_counts)
        Dead time optimization for Si detectors: 15-25% optimal
        """
        # For 2% RSD, need ~2500 total counts
        # For 1% RSD, need ~10000 total counts
        required_counts = (100 / target_precision_rsd)**2
        
        # Si detector dead time calculations
        # Dead time = (input_rate × dead_time_constant) / (1 + input_rate × dead_time_constant)
        # Typical Si detector dead time constant: ~1-3 μs
        dead_time_constant = 2.0e-6  # 2 μs typical for Si detector
        
        # Calculate input count rate for target dead time
        target_dead_time_fraction = target_dead_time / 100
        optimal_input_rate = target_dead_time_fraction / (dead_time_constant * (1 - target_dead_time_fraction))
        
        # XRF instrument parameters
        xrf_conditions = {
            'tube_voltage_kV': 50,
            'tube_current': 'Auto (optimize for dead time)',
            'beam_size_mm': 1.2,
            'filters': 'None',
            'target_dead_time_%': f'{target_dead_time:.1f}',
            'optimal_input_count_rate_cps': f'{optimal_input_rate:.0f}',
            'measurement_time_seconds': 30,
            'live_time_vs_real_time': f'Live time = Real time × (1 - dead_time/100)',
            'minimum_total_counts': required_counts,
            'replicate_measurements': 'Minimum 3, recommended 6 per sample'
        }
        
        # Calculate actual measurement statistics
        effective_count_rate = optimal_input_rate * (1 - target_dead_time_fraction)
        total_counts_30s = effective_count_rate * 30
        achieved_precision = 100 / np.sqrt(total_counts_30s)
        
        xrf_conditions.update({
            'effective_count_rate_cps': f'{effective_count_rate:.0f}',
            'total_counts_30s': f'{total_counts_30s:.0f}',
            'achieved_precision_rsd_%': f'{achieved_precision:.2f}'
        })
        
        return xrf_conditions
    
    def generate_sop(self):
        """Generate Standard Operating Procedure document"""
        sop = """
STANDARD OPERATING PROCEDURE: XRF Analysis of Pb in Pressed Pellets

1. SAMPLE PREPARATION
   a) Grind sample to uniform particle size (<75 μm)
   b) Weigh 2.000 ± 0.001 g of ground sample
   c) Weigh 0.400 ± 0.001 g of binder
   d) Mix thoroughly for 2 minutes
   e) Record sample ID, masses, and preparation date

2. PELLET PRESSING
   a) Clean die with appropriate solvent
   b) Transfer mixture to 15mm die
   c) Apply 5 tons pressure for 5 minutes
   d) Remove pellet and inspect for defects
   e) Weigh pellet (target: 2.40 ± 0.05 g)

3. XRF INSTRUMENT SETUP
   a) X-ray tube voltage: 50 kV
   b) X-ray tube current: Auto (optimize for 15-25% dead time)
   c) Beam size: 1.2 mm
   d) Filters: None
   e) Detector: Si detector
   f) Target dead time: 20% ± 5%

4. XRF MEASUREMENT
   a) Position pellet in sample holder (ensure 1.2mm beam hits sample)
   b) Optimize tube current to achieve 15-25% dead time
   c) Measure for 30 seconds (measurement time, not real time)
   d) Record dead time percentage for each measurement
   e) Collect 6 replicate measurements minimum
   f) Monitor count rate stability during measurement

5. DATA ANALYSIS
   a) Verify dead time was within 15-25% range
   b) Calculate mean integrated intensity from live time data
   c) Apply calibration: Conc = 13.8913 × Intensity + 0
   d) Correct for dilution factor: Original_Conc = Pellet_Conc / 0.833
   e) Calculate statistics (mean, SD, RSD)
   f) Report results with uncertainty

6. QUALITY CONTROL
   a) Analyze reference material every 10 samples
   b) Analyze blank pellet (binder only) daily
   c) Check dead time optimization weekly
   d) Verify beam positioning with alignment standards
   e) Monitor tube current stability
   f) Document any deviations or issues

7. TROUBLESHOOTING
   a) If dead time <15%: Increase tube current or check sample positioning
   b) If dead time >25%: Decrease tube current or check for contamination
   c) If count rate unstable: Check tube stability and sample surface
   d) If poor precision: Verify pellet homogeneity and measurement statistics
"""
        return sop

# Example usage
def validate_protocol():
    """Example validation of the pellet protocol"""
    
    analyzer = PelletBasedXRFAnalysis()
    
    # Generate protocol checklist
    checklist = analyzer.protocol_validation_checklist()
    print("PELLET PREPARATION PROTOCOL VALIDATION")
    print("=" * 50)
    
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ☐ {item}")
    
    # Calculate uncertainty budget
    uncertainty = analyzer.estimate_uncertainty_budget()
    print(f"\nUNCERTAINTY BUDGET")
    print("=" * 30)
    for source, value in uncertainty.items():
        print(f"{source}: {value:.2f}")
    
    # Measurement optimization
    optimization = analyzer.optimize_measurement_conditions(target_precision_rsd=2.0)
    print(f"\nMEASUREMENT OPTIMIZATION")
    print("=" * 35)
    for param, value in optimization.items():
        print(f"{param}: {value}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = validate_protocol()
