#!/usr/bin/env python3
"""
Test the fixed parser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import parse_xrf_file_smart

# Test with synthetic file
test_file = "/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb/test_spectra/Zn_Till_1_synthetic.csv"

if os.path.exists(test_file):
    print(f"Testing parser with: {test_file}")
    
    try:
        x, y, format_type = parse_xrf_file_smart(test_file)
        if x is not None and y is not None:
            print(f"✅ Parser works: {len(x)} data points, format: {format_type}")
            print(f"   Energy range: {x.min():.2f} - {x.max():.2f} keV")
            print(f"   Intensity range: {y.min():.0f} - {y.max():.0f} counts")
        else:
            print("❌ Parser failed")
    except Exception as e:
        print(f"❌ Parser error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Test file not found")
