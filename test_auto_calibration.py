#!/usr/bin/env python3
"""
Test script for automatic multi-element calibration functionality
"""

import sys
import os
import numpy as np
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import ELEMENT_DEFINITIONS, REFERENCE_MATERIALS, XRFPeakFitter

def create_synthetic_spectrum(element, concentration, noise_level=0.1):
    """Create a synthetic XRF spectrum for testing"""
    element_data = ELEMENT_DEFINITIONS[element]
    primary_energy = element_data['primary_energy']
    
    # Create energy array (0.5 to 30 keV, typical XRF range)
    energy = np.linspace(0.5, 30.0, 3000)
    
    # Create baseline spectrum with some background
    baseline = 1000 * np.exp(-energy/10) + 50  # Exponential background
    
    # Add the main peak (Gaussian)
    peak_intensity = concentration * 10 + 100  # Scale with concentration
    peak_width = 0.15  # FWHM in keV
    main_peak = peak_intensity * np.exp(-0.5 * ((energy - primary_energy) / peak_width)**2)
    
    # Add secondary peak if present
    if 'secondary_energy' in element_data:
        secondary_energy = element_data['secondary_energy']
        secondary_intensity = peak_intensity * 0.3  # Secondary peak is weaker
        secondary_peak = secondary_intensity * np.exp(-0.5 * ((energy - secondary_energy) / peak_width)**2)
        baseline += secondary_peak
    
    # Combine baseline and main peak
    spectrum = baseline + main_peak
    
    # Add Poisson noise
    if noise_level > 0:
        noise = np.random.poisson(spectrum * noise_level) - spectrum * noise_level
        spectrum += noise
    
    # Ensure no negative values
    spectrum = np.maximum(spectrum, 1)
    
    return energy, spectrum

def create_test_spectra_files(element, output_dir):
    """Create synthetic spectra files for testing"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get available standards for this element
    available_standards = []
    concentrations = []
    
    for material_name, material_data in REFERENCE_MATERIALS.items():
        value = material_data.get(element)
        if value is not None and value != "N/A":
            try:
                if isinstance(value, str):
                    if '%' in value:
                        if '<' in value:
                            continue
                        conc = float(value.replace('%', '')) * 10000  # Convert % to ppm
                    else:
                        conc = float(value)
                else:
                    conc = float(value)
                
                available_standards.append(material_name)
                concentrations.append(conc)
            except (ValueError, TypeError):
                continue
    
    created_files = []
    
    # Create synthetic spectra for each standard
    for standard, conc in zip(available_standards, concentrations):
        energy, intensity = create_synthetic_spectrum(element, conc)
        
        # Create filename
        filename = f"{element}_{standard.replace(' ', '_')}_synthetic.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save as CSV
        df = pd.DataFrame({
            'Energy_keV': energy,
            'Intensity': intensity
        })
        df.to_csv(filepath, index=False)
        
        created_files.append((standard, conc, filepath))
        print(f"Created: {filename} (Concentration: {conc:.2f} ppm)")
    
    return created_files

def test_peak_fitting_on_synthetic_data(element, test_files):
    """Test peak fitting on synthetic data"""
    print(f"\nTesting peak fitting for {element}:")
    print("=" * 50)
    
    fitter = XRFPeakFitter(element=element)
    
    measured_intensities = []
    true_concentrations = []
    
    for standard, true_conc, filepath in test_files:
        try:
            # Load the synthetic data
            df = pd.read_csv(filepath)
            energy = df['Energy_keV'].values
            intensity = df['Intensity'].values
            
            # Fit the peak
            fit_params, fit_curve, r_squared, x_fit, integrated_intensity, calculated_conc = fitter.fit_peak(
                energy, intensity,
                peak_region=None,  # Use element defaults
                background_subtract=True,
                integration_region=None  # Use element defaults
            )
            
            measured_intensities.append(integrated_intensity)
            true_concentrations.append(true_conc)
            
            print(f"{standard}:")
            print(f"  True Concentration: {true_conc:.2f} ppm")
            print(f"  Integrated Intensity: {integrated_intensity:.2f}")
            print(f"  Fit R²: {r_squared:.4f}")
            print(f"  Peak Center: {fit_params['center']:.3f} keV (expected: {fitter.target_energy:.3f})")
            
        except Exception as e:
            print(f"{standard}: Error - {e}")
    
    # Test calibration creation
    if len(measured_intensities) >= 2:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(measured_intensities, true_concentrations)
        
        print(f"\nCalibration Results:")
        print(f"Equation: Concentration = {slope:.4f} × Intensity + {intercept:.4f}")
        print(f"R² = {r_value**2:.4f}")
        print(f"Standard Error = {std_err:.4f}")
        
        # Test the calibration
        print(f"\nCalibration Validation:")
        for i, (standard, true_conc, _) in enumerate(test_files[:len(measured_intensities)]):
            predicted_conc = slope * measured_intensities[i] + intercept
            error = abs(predicted_conc - true_conc) / true_conc * 100
            print(f"  {standard}: True={true_conc:.1f}, Predicted={predicted_conc:.1f}, Error={error:.1f}%")
    
    return measured_intensities, true_concentrations

def main():
    print("Testing Automatic Multi-Element Calibration")
    print("=" * 60)
    
    # Test directory
    test_dir = "/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb/test_spectra"
    
    # Test elements with good standard coverage
    test_elements = ['Zn', 'Cr', 'Ni', 'Cu']
    
    for element in test_elements:
        print(f"\n🧪 Testing {element} ({ELEMENT_DEFINITIONS[element]['name']}):")
        print(f"Primary Energy: {ELEMENT_DEFINITIONS[element]['primary_energy']} keV")
        
        # Create synthetic test files
        test_files = create_test_spectra_files(element, test_dir)
        
        if len(test_files) >= 2:
            # Test peak fitting and calibration
            intensities, concentrations = test_peak_fitting_on_synthetic_data(element, test_files)
            print(f"✅ Successfully tested {element} with {len(test_files)} standards")
        else:
            print(f"❌ Insufficient standards for {element} ({len(test_files)} available)")
        
        print("-" * 50)
    
    print(f"\n📁 Test files created in: {test_dir}")
    print("You can now test the GUI with these synthetic spectra files!")

if __name__ == "__main__":
    main()
