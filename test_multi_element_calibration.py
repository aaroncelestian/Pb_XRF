#!/usr/bin/env python3
"""
Test the multi-element calibration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import ELEMENT_DEFINITIONS, REFERENCE_MATERIALS

def test_multi_element_calibration_logic():
    """Test the logic for finding calibratable elements"""
    print("Testing Multi-Element Calibration Logic")
    print("=" * 50)
    
    # Find elements with sufficient standards (at least 2)
    calibratable_elements = []
    
    for element in ELEMENT_DEFINITIONS.keys():
        available_standards = []
        concentrations = []
        
        for material_name, material_data in REFERENCE_MATERIALS.items():
            value = material_data.get(element)
            if value is not None and value != "N/A":
                try:
                    if isinstance(value, str):
                        if '%' in value:
                            if '<' in value:
                                continue  # Skip below detection limit values
                            conc = float(value.replace('%', '')) * 10000  # Convert % to ppm
                        else:
                            conc = float(value)
                    else:
                        conc = float(value)
                    
                    available_standards.append(material_name)
                    concentrations.append(conc)
                except (ValueError, TypeError):
                    continue
        
        if len(available_standards) >= 2:
            calibratable_elements.append((element, available_standards, concentrations))
    
    print(f"Found {len(calibratable_elements)} calibratable elements:")
    print()
    
    for element, standards, concentrations in calibratable_elements:
        element_name = ELEMENT_DEFINITIONS[element]['name']
        energy = ELEMENT_DEFINITIONS[element]['primary_energy']
        min_conc = min(concentrations)
        max_conc = max(concentrations)
        
        print(f"🔹 {element} ({element_name}) - {energy} keV")
        print(f"   Standards: {len(standards)} ({', '.join(standards)})")
        print(f"   Range: {min_conc:.1f} - {max_conc:.1f} ppm")
        print()
    
    # Get all unique reference materials needed
    all_materials = set()
    for element, standards, concentrations in calibratable_elements:
        all_materials.update(standards)
    
    all_materials = sorted(list(all_materials))
    
    print(f"📁 Reference materials needed: {len(all_materials)}")
    for material in all_materials:
        print(f"   - {material}")
    
    print()
    print("🎯 Multi-element calibration would analyze:")
    print(f"   - {len(all_materials)} reference material files")
    print(f"   - {len(calibratable_elements)} elements per file")
    print(f"   - Total: {len(all_materials) * len(calibratable_elements)} peak fits")
    
    return calibratable_elements, all_materials

if __name__ == "__main__":
    calibratable_elements, all_materials = test_multi_element_calibration_logic()
    
    print("\n" + "=" * 50)
    print("Multi-element calibration logic test complete!")
    print(f"Ready to calibrate {len(calibratable_elements)} elements using {len(all_materials)} reference materials.")
