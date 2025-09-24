#!/usr/bin/env python3
"""
Test script for multi-element XRF calibration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import ELEMENT_DEFINITIONS, REFERENCE_MATERIALS, XRFPeakFitter

def test_element_definitions():
    """Test that all elements are properly defined"""
    print("Testing Element Definitions...")
    
    expected_elements = ['Pb', 'As', 'Cd', 'Cr', 'Zn', 'Ni', 'Cu', 'Fe', 'Se', 'S']
    
    for element in expected_elements:
        if element in ELEMENT_DEFINITIONS:
            element_data = ELEMENT_DEFINITIONS[element]
            print(f"✓ {element} ({element_data['name']}) - Energy: {element_data['primary_energy']} keV")
            
            # Check required fields
            required_fields = ['name', 'symbol', 'primary_energy', 'peak_region', 'integration_region', 'default_calibration']
            for field in required_fields:
                if field not in element_data:
                    print(f"  ✗ Missing field: {field}")
                else:
                    print(f"  ✓ {field}: {element_data[field]}")
        else:
            print(f"✗ {element} not found in definitions")
    
    print()

def test_reference_materials():
    """Test reference materials data"""
    print("Testing Reference Materials...")
    
    materials = list(REFERENCE_MATERIALS.keys())
    elements = list(ELEMENT_DEFINITIONS.keys())
    
    print(f"Available materials: {materials}")
    print(f"Available elements: {elements}")
    
    # Count available data points for each element
    for element in elements:
        available_count = 0
        available_materials = []
        
        for material in materials:
            value = REFERENCE_MATERIALS[material].get(element)
            if value is not None and value != "N/A":
                available_count += 1
                available_materials.append(material)
        
        print(f"{element}: {available_count} standards available ({', '.join(available_materials)})")
    
    print()

def test_peak_fitter():
    """Test XRFPeakFitter multi-element functionality"""
    print("Testing XRFPeakFitter...")
    
    # Test initialization with different elements
    for element in ['Pb', 'As', 'Zn', 'Cu']:
        fitter = XRFPeakFitter(element=element)
        element_data = ELEMENT_DEFINITIONS[element]
        
        print(f"Testing {element}:")
        print(f"  Target Energy: {fitter.target_energy} (expected: {element_data['primary_energy']})")
        print(f"  Calibration Slope: {fitter.calibration_slope}")
        print(f"  Calibration Intercept: {fitter.calibration_intercept}")
        
        # Test element switching
        if element != 'Fe':
            fitter.set_element('Fe')
            fe_data = ELEMENT_DEFINITIONS['Fe']
            print(f"  After switching to Fe - Target Energy: {fitter.target_energy} (expected: {fe_data['primary_energy']})")
        
        print()

def test_calibration_data_parsing():
    """Test parsing of reference material concentration data"""
    print("Testing Calibration Data Parsing...")
    
    test_element = 'Pb'
    available_standards = []
    concentrations = []
    
    for material_name, material_data in REFERENCE_MATERIALS.items():
        value = material_data.get(test_element)
        if value is not None and value != "N/A":
            try:
                if isinstance(value, str):
                    # Handle percentage values
                    if '%' in value:
                        if '<' in value:
                            print(f"  {material_name}: Below detection limit ({value})")
                            continue
                        conc = float(value.replace('%', '')) * 10000  # Convert % to ppm
                        print(f"  {material_name}: {value} → {conc} ppm")
                    else:
                        conc = float(value)
                        print(f"  {material_name}: {conc} ppm")
                else:
                    conc = float(value)
                    print(f"  {material_name}: {conc} ppm")
                
                available_standards.append(material_name)
                concentrations.append(conc)
            except (ValueError, TypeError) as e:
                print(f"  {material_name}: Error parsing '{value}' - {e}")
    
    print(f"\nUsable standards for {test_element}: {len(available_standards)}")
    print(f"Concentration range: {min(concentrations):.1f} - {max(concentrations):.1f} ppm")
    print()

if __name__ == "__main__":
    print("Multi-Element XRF Calibration Test")
    print("=" * 40)
    
    test_element_definitions()
    test_reference_materials()
    test_peak_fitter()
    test_calibration_data_parsing()
    
    print("All tests completed!")
