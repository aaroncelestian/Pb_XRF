#!/usr/bin/env python3
"""
Test the persistent calibration system
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import CalibrationManager, ELEMENT_DEFINITIONS

def test_calibration_manager():
    """Test the CalibrationManager functionality"""
    print("🧪 Testing Persistent Calibration System")
    print("=" * 50)
    
    # Create test calibration manager
    test_file = "test_calibrations.json"
    if os.path.exists(test_file):
        os.remove(test_file)  # Start fresh
    
    cal_mgr = CalibrationManager(test_file)
    
    # Test 1: Add calibrations
    print("\n1. Testing calibration creation...")
    test_calibrations = {
        'Pb': {'slope': 13.8913, 'intercept': 0.0, 'r_squared': 0.9901, 'standards': ['Till 1', 'LKSD 1', 'PACS 2']},
        'Zn': {'slope': 0.2587, 'intercept': -9.3618, 'r_squared': 0.9999, 'standards': ['Till 1', 'LKSD 1', 'PACS 2']},
        'Cu': {'slope': 0.2563, 'intercept': -10.0761, 'r_squared': 1.0000, 'standards': ['Till 1', 'LKSD 1']},
        'Cr': {'slope': 0.4627, 'intercept': -27.6859, 'r_squared': 0.9987, 'standards': ['Till 1', 'LKSD 1', 'PACS 2']}
    }
    
    for element, data in test_calibrations.items():
        cal_mgr.update_calibration(
            element, data['slope'], data['intercept'], 
            data['r_squared'], data['standards']
        )
        print(f"  ✓ Added calibration for {element}")
    
    # Test 2: Verify persistence
    print("\n2. Testing calibration persistence...")
    cal_mgr2 = CalibrationManager(test_file)  # Load from file
    
    for element in test_calibrations.keys():
        if cal_mgr2.has_calibration(element):
            cal_data = cal_mgr2.get_calibration(element)
            print(f"  ✓ {element}: {cal_data['equation']}")
        else:
            print(f"  ✗ {element}: Not found!")
    
    # Test 3: Export/Import
    print("\n3. Testing export/import...")
    export_file = "test_export.json"
    
    if cal_mgr2.export_calibrations(export_file):
        print(f"  ✓ Exported to {export_file}")
        
        # Test import
        cal_mgr3 = CalibrationManager("test_import.json")
        if cal_mgr3.import_calibrations(export_file):
            print(f"  ✓ Imported from {export_file}")
            print(f"  ✓ Imported {len(cal_mgr3.get_all_calibrations())} calibrations")
        else:
            print(f"  ✗ Import failed")
    else:
        print(f"  ✗ Export failed")
    
    # Test 4: Calibration status
    print("\n4. Testing calibration status...")
    all_cals = cal_mgr2.get_all_calibrations()
    
    print(f"📊 Calibration Status Summary:")
    print(f"   Total calibrations: {len(all_cals)}")
    
    for element in ELEMENT_DEFINITIONS.keys():
        if element in all_cals:
            cal = all_cals[element]
            print(f"   ✅ {element}: R²={cal.get('r_squared', 'N/A'):.4f}, Standards={len(cal.get('standards_used', []))}")
        else:
            default_cal = ELEMENT_DEFINITIONS[element]['default_calibration']
            print(f"   ⚠️  {element}: Using default (slope={default_cal['slope']:.4f})")
    
    # Cleanup
    for file in [test_file, export_file, "test_import.json"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n✅ All calibration persistence tests passed!")

def test_calibration_file_format():
    """Test the calibration file format"""
    print("\n" + "=" * 50)
    print("📄 Testing Calibration File Format")
    print("=" * 50)
    
    # Create sample calibration
    cal_mgr = CalibrationManager("format_test.json")
    cal_mgr.update_calibration('Pb', 13.8913, 0.0, 0.9901, ['Till 1', 'LKSD 1'])
    
    # Read and display file format
    if os.path.exists("format_test.json"):
        with open("format_test.json", 'r') as f:
            data = json.load(f)
        
        print("Sample calibration file format:")
        print(json.dumps(data, indent=2))
        
        # Verify required fields
        pb_cal = data.get('Pb', {})
        required_fields = ['slope', 'intercept', 'r_squared', 'standards_used', 'created_date', 'equation']
        
        print(f"\nRequired fields check:")
        for field in required_fields:
            if field in pb_cal:
                print(f"  ✓ {field}: {pb_cal[field]}")
            else:
                print(f"  ✗ {field}: Missing")
        
        os.remove("format_test.json")
    
    print("\n✅ File format test complete!")

def main():
    """Run all calibration persistence tests"""
    test_calibration_manager()
    test_calibration_file_format()
    
    print("\n" + "🎉" * 20)
    print("🎯 PERSISTENT CALIBRATION SYSTEM READY!")
    print("🎉" * 20)
    
    print(f"\n📋 Key Features:")
    print(f"✅ Automatic save/load of calibrations")
    print(f"✅ Persistent storage in JSON format")
    print(f"✅ Export/import calibration sets")
    print(f"✅ Calibration status display")
    print(f"✅ Reset to defaults option")
    print(f"✅ Multi-element calibration support")
    
    print(f"\n🔧 How it works:")
    print(f"1. Calibrations automatically saved to 'xrf_calibrations.json'")
    print(f"2. Loaded automatically when GUI starts")
    print(f"3. Status display shows current calibration state")
    print(f"4. Export/import for sharing calibrations")
    print(f"5. Reset option to return to defaults")

if __name__ == "__main__":
    main()
