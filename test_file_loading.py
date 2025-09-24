#!/usr/bin/env python3
"""
Test file loading functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import XRFPeakFittingGUI, parse_xrf_file_smart

def test_file_loading():
    """Test that file loading works correctly"""
    print("Testing file loading functionality...")
    
    # Test with synthetic files
    test_dir = "/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb/test_spectra"
    
    if os.path.exists(test_dir):
        test_files = [f for f in os.listdir(test_dir) if f.endswith('.csv')]
        
        if test_files:
            test_file = os.path.join(test_dir, test_files[0])
            print(f"Testing with: {test_file}")
            
            # Test the smart parser directly
            try:
                x, y, format_type = parse_xrf_file_smart(test_file)
                if x is not None and y is not None:
                    print(f"✅ Smart parser works: {len(x)} data points, format: {format_type}")
                    print(f"   Energy range: {x.min():.2f} - {x.max():.2f} keV")
                    print(f"   Intensity range: {y.min():.0f} - {y.max():.0f} counts")
                else:
                    print("❌ Smart parser failed")
            except Exception as e:
                print(f"❌ Smart parser error: {e}")
            
            # Test the GUI method
            try:
                gui = XRFPeakFittingGUI()
                data = gui.read_xrf_file(test_file)
                if data is not None:
                    x, y = data
                    print(f"✅ GUI read_xrf_file works: {len(x)} data points")
                else:
                    print("❌ GUI read_xrf_file failed")
            except Exception as e:
                print(f"❌ GUI read_xrf_file error: {e}")
        else:
            print("No test files found")
    else:
        print("Test directory not found")
    
    # Test with any existing files in the main directory
    main_files = [f for f in os.listdir("/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb") 
                  if f.endswith(('.txt', '.csv')) and 'test' not in f.lower()]
    
    if main_files:
        test_file = os.path.join("/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb", main_files[0])
        print(f"\nTesting with real file: {test_file}")
        
        try:
            x, y, format_type = parse_xrf_file_smart(test_file)
            if x is not None and y is not None:
                print(f"✅ Real file parsing works: {len(x)} data points, format: {format_type}")
            else:
                print("❌ Real file parsing failed")
        except Exception as e:
            print(f"❌ Real file parsing error: {e}")

if __name__ == "__main__":
    test_file_loading()
