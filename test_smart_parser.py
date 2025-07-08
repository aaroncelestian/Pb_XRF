#!/usr/bin/env python3
"""
Test script for the smart XRF file parser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xrf_Pb_analysis import parse_xrf_file_smart, detect_file_format
import numpy as np

def test_nist_standard_files():
    """Test parsing of NIST standard files"""
    print("Testing NIST Standard Files:")
    print("=" * 50)
    
    nist_files = [
        "nist_pb_standards/STD3000-1.txt",
        "nist_pb_standards/STD3000-2.txt", 
        "nist_pb_standards/STD3000-3.txt",
        "nist_pb_standards/STD500-1.txt",
        "nist_pb_standards/STD500-2.txt",
        "nist_pb_standards/STD500-3.txt"
    ]
    
    for file_path in nist_files:
        if os.path.exists(file_path):
            print(f"\nTesting: {file_path}")
            
            # Test format detection
            format_type = detect_file_format(file_path)
            print(f"  Detected format: {format_type}")
            
            # Test parsing
            x, y, detected_format = parse_xrf_file_smart(file_path)
            
            if x is not None and y is not None:
                print(f"  ✅ Successfully parsed!")
                print(f"  Data points: {len(x)}")
                print(f"  Energy range: {x.min():.2f} to {x.max():.2f} keV")
                print(f"  Intensity range: {y.min():.2f} to {y.max():.2f} counts")
                print(f"  Detected format: {detected_format}")
            else:
                print(f"  ❌ Failed to parse!")
        else:
            print(f"\n⚠️  File not found: {file_path}")

def test_other_formats():
    """Test parsing of other file formats"""
    print("\n\nTesting Other File Formats:")
    print("=" * 50)
    
    other_files = [
        "LC2030623EE-1.txt",
        "LC2030623EE-2.txt", 
        "LC2030623EE-3.txt",
        "example_standards/SRM_2586_replicate_1.txt",
        "example_standards/SRM_2587_replicate_1.txt"
    ]
    
    for file_path in other_files:
        if os.path.exists(file_path):
            print(f"\nTesting: {file_path}")
            
            # Test format detection
            format_type = detect_file_format(file_path)
            print(f"  Detected format: {format_type}")
            
            # Test parsing
            x, y, detected_format = parse_xrf_file_smart(file_path)
            
            if x is not None and y is not None:
                print(f"  ✅ Successfully parsed!")
                print(f"  Data points: {len(x)}")
                print(f"  Energy range: {x.min():.2f} to {x.max():.2f} keV")
                print(f"  Intensity range: {y.min():.2f} to {y.max():.2f} counts")
                print(f"  Detected format: {detected_format}")
            else:
                print(f"  ❌ Failed to parse!")
        else:
            print(f"\n⚠️  File not found: {file_path}")

if __name__ == "__main__":
    print("Smart XRF File Parser Test")
    print("=" * 60)
    
    test_nist_standard_files()
    test_other_formats()
    
    print("\n\nTest completed!") 