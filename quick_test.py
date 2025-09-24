#!/usr/bin/env python3
"""
Quick test of file reading
"""

import sys
import os
import pandas as pd
import numpy as np

# Test reading one of our synthetic files
test_file = "/Users/aaroncelestian/Library/CloudStorage/Dropbox/Python/XRF_Pb/test_spectra/Zn_Till_1_synthetic.csv"

if os.path.exists(test_file):
    print(f"Testing file: {test_file}")
    
    # Test pandas reading
    try:
        df = pd.read_csv(test_file)
        print(f"✅ Pandas read successful: {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())
        
        # Extract data
        if 'Energy_keV' in df.columns and 'Intensity' in df.columns:
            x = df['Energy_keV'].values
            y = df['Intensity'].values
            print(f"✅ Data extraction successful: {len(x)} points")
            print(f"Energy range: {x.min():.2f} - {x.max():.2f} keV")
            print(f"Intensity range: {y.min():.0f} - {y.max():.0f} counts")
        else:
            print("❌ Expected columns not found")
            
    except Exception as e:
        print(f"❌ Pandas error: {e}")
else:
    print("Test file not found")
