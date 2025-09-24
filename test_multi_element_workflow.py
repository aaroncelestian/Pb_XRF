#!/usr/bin/env python3
"""
Test the multi-element workflow functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import ELEMENT_DEFINITIONS

def test_multi_element_workflow():
    """Test the multi-element workflow logic"""
    print("Testing Multi-Element Workflow")
    print("=" * 50)
    
    # Test element selection
    print("Available elements for selection:")
    for element, data in ELEMENT_DEFINITIONS.items():
        print(f"  ✓ {element} ({data['name']}) - {data['primary_energy']} keV")
    
    print(f"\nTotal elements available: {len(ELEMENT_DEFINITIONS)}")
    
    # Test element groupings
    common_elements = ['Pb', 'Zn', 'Cu', 'Cr']
    print(f"\nCommon elements: {common_elements}")
    
    all_elements = list(ELEMENT_DEFINITIONS.keys())
    print(f"All elements: {all_elements}")
    
    # Test workflow scenarios
    print("\n" + "=" * 50)
    print("WORKFLOW SCENARIOS")
    print("=" * 50)
    
    print("\n1. Single Element Analysis (Traditional):")
    print("   - Select: Pb only")
    print("   - Result: Pb concentrations for all samples")
    
    print("\n2. Common Elements Analysis:")
    print("   - Select: Pb, Zn, Cu, Cr")
    print("   - Result: 4 elements × N samples = comprehensive analysis")
    
    print("\n3. Full Multi-Element Analysis:")
    print("   - Select: All 10 elements")
    print("   - Result: Complete elemental profile for all samples")
    
    print("\n4. Custom Selection:")
    print("   - Select: User-defined subset")
    print("   - Result: Targeted analysis for specific research needs")
    
    print("\n" + "=" * 50)
    print("EXPECTED WORKFLOW")
    print("=" * 50)
    
    print("\n1. User selects elements in Main Workflow tab")
    print("2. User selects folder with XRF files")
    print("3. User clicks 'Process Batch'")
    print("4. System analyzes each file for all selected elements")
    print("5. Results show concentrations for each element per sample")
    print("6. Statistics calculated separately for each element")
    
    print("\nExample output for 3 elements, 2 samples:")
    print("Sample_1:")
    print("  Pb (Lead): 125.3 ± 5.2 ppm (RSD: 4.1%)")
    print("  Zn (Zinc): 89.7 ± 3.1 ppm (RSD: 3.5%)")
    print("  Cu (Copper): 45.2 ± 2.8 ppm (RSD: 6.2%)")
    print("Sample_2:")
    print("  Pb (Lead): 98.1 ± 4.7 ppm (RSD: 4.8%)")
    print("  Zn (Zinc): 156.3 ± 7.2 ppm (RSD: 4.6%)")
    print("  Cu (Copper): 67.9 ± 5.1 ppm (RSD: 7.5%)")

if __name__ == "__main__":
    test_multi_element_workflow()
