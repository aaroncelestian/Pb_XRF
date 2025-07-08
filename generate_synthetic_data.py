import numpy as np
import os
from datetime import datetime, timedelta
import random

def generate_synthetic_xrf_data(target_concentration_ppm, output_filename, base_spectrum=None):
    """
    Generate synthetic XRF data with specified Pb concentration
    
    Parameters:
    - target_concentration_ppm: Target Pb concentration in ppm
    - output_filename: Name of output file
    - base_spectrum: Optional base spectrum to modify (for realistic background)
    
    Returns:
    - None (writes file to disk)
    """
    
    # Energy range and resolution (matching real data)
    energy_start = -0.4
    energy_end = 40.0
    energy_step = 0.01
    energies = np.arange(energy_start, energy_end + energy_step, energy_step)
    n_points = len(energies)
    
    # Pb L-alpha peak parameters
    pb_peak_energy = 10.52  # keV
    pb_peak_fwhm = 0.15    # keV (typical for XRF)
    
    # Generate base background spectrum (realistic XRF background)
    if base_spectrum is None:
        # Create realistic background with multiple components
        background = np.zeros_like(energies)
        
        # Exponential decay background
        background += 50 * np.exp(-energies / 5.0)
        
        # Linear component
        background += 10 + 2 * energies
        
        # Add some noise and structure
        np.random.seed(42)  # For reproducible results
        noise = np.random.poisson(background * 0.1)
        background += noise
        
        # Add some characteristic XRF features
        # Compton scatter peak around 9.5 keV
        compton_peak = 100 * np.exp(-((energies - 9.5) / 0.3)**2)
        background += compton_peak
        
        # Bremsstrahlung continuum
        brems = 30 * np.exp(-energies / 15.0)
        background += brems
        
    else:
        background = base_spectrum.copy()
    
    # Calculate peak amplitude based on concentration
    # Using the calibration: Concentration = 13.8913 * AVE_I + 0
    # We need to work backwards to get the integrated intensity
    target_integrated_intensity = target_concentration_ppm / 13.8913
    
    # For Gaussian-A function, the integrated area is: A * FWHM * sqrt(pi/ln(2))
    # So amplitude = integrated_intensity / (FWHM * sqrt(pi/ln(2)))
    ln2 = np.log(2)
    amplitude = target_integrated_intensity / (pb_peak_fwhm * np.sqrt(np.pi / ln2))
    
    # Generate Pb peak
    pb_peak = amplitude * np.sqrt(ln2 / np.pi) / pb_peak_fwhm * np.exp(-ln2 * ((energies - pb_peak_energy) / pb_peak_fwhm)**2)
    
    # Add peak to background
    spectrum = background + pb_peak
    
    # Add realistic counting statistics (Poisson noise)
    spectrum = np.random.poisson(spectrum)
    
    # Ensure no negative values
    spectrum = np.maximum(spectrum, 0)
    
    # Generate metadata
    current_time = datetime.now()
    file_time = current_time + timedelta(minutes=random.randint(0, 1440))
    
    # Write to file in EMSA format
    with open(output_filename, 'w') as f:
        f.write("#FORMAT      : EMSA/MAS Spectral Data File\n")
        f.write("#VERSION     : 1.0\n")
        f.write(f"#TITLE       : {os.path.splitext(os.path.basename(output_filename))[0]}\n")
        f.write(f"#DATE        : {file_time.strftime('%d-%b-%Y')}\n")
        f.write(f"#TIME        : {file_time.strftime('%H:%M')}\n")
        f.write("#OWNER       : XGT7200\n")
        f.write(f"#NPOINTS     : {n_points}.\n")
        f.write("#NCOLUMNS    : 1.\n")
        f.write("#XUNITS      : keV\n")
        f.write("#YUNITS      : counts\n")
        f.write("#DATATYPE    : XY\n")
        f.write("#XPERCHAN    : 0.0100000\n")
        f.write("#OFFSET      : -0.400000\n")
        f.write("#SIGNALTYPE  : EDS\n")
        f.write("#CHOFFSET    : 40.0000\n")
        f.write("#LIVETIME    : 30.000000\n")
        f.write("#REALTIME    : 39.525036\n")
        f.write("#BEAMKV      : 50.0000\n")
        f.write("#PROBECUR    : 596000.\n")
        f.write("#MAGCAM      : 100.000\n")
        f.write("#XTILTSTGE   : 0.0\n")
        f.write("#AZIMANGLE   : 0.0\n")
        f.write("#ELEVANGLE   : 45.0\n")
        f.write("#XPOSITION mm: 0.0000\n")
        f.write("#YPOSITION mm: 0.0000\n")
        f.write("#ZPOSITION mm: 0.0000\n")
        f.write("##OXINSTPT   : 4\n")
        f.write("##OXINSTSTROB: 72.02\n")
        f.write("#SPECTRUM    : Spectral Data Starts Here\n")
        
        # Write spectral data
        for i, (energy, intensity) in enumerate(zip(energies, spectrum)):
            f.write(f"{energy:.5f}, {intensity:.0f}.\n")
    
    return spectrum

def create_concentration_range_datasets():
    """
    Create 100 synthetic datasets with Pb concentrations from 0 to 2000 ppm
    """
    
    # Create output directory
    output_dir = "synthetic_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate concentration range
    # Use logarithmic spacing for better distribution across the range
    concentrations = np.logspace(0, np.log10(2000), 100)
    
    # Also add some zero concentration samples
    concentrations = np.concatenate([np.zeros(10), concentrations])
    
    # Shuffle to randomize order
    np.random.shuffle(concentrations)
    
    # Generate base spectrum from one of the real files for realistic background
    try:
        # Read a real file to get realistic background
        real_data = np.loadtxt("LC2030623EE-1.txt", skiprows=25, delimiter=", ")
        real_energies = real_data[:, 0]
        real_intensities = real_data[:, 1]
        
        # Interpolate to match our energy grid
        from scipy.interpolate import interp1d
        energy_start = -0.4
        energy_end = 40.0
        energy_step = 0.01
        energies = np.arange(energy_start, energy_end + energy_step, energy_step)
        
        # Only use the background region (avoid the Pb peak)
        bg_mask = (real_energies < 10.0) | (real_energies > 11.0)
        bg_energies = real_energies[bg_mask]
        bg_intensities = real_intensities[bg_mask]
        
        # Interpolate background
        bg_interp = interp1d(bg_energies, bg_intensities, 
                            bounds_error=False, fill_value=0)
        base_spectrum = bg_interp(energies)
        
        # Fill any NaN values
        base_spectrum = np.nan_to_num(base_spectrum, nan=0.0)
        
    except:
        print("Warning: Could not read real data file, using synthetic background")
        base_spectrum = None
    
    # Generate all datasets
    print(f"Generating {len(concentrations)} synthetic XRF datasets...")
    
    results = []
    for i, concentration in enumerate(concentrations):
        filename = f"synthetic_data/SYNTH_{i+1:03d}_{concentration:.1f}ppm.txt"
        
        print(f"Generating {filename} (Pb: {concentration:.1f} ppm)")
        
        spectrum = generate_synthetic_xrf_data(concentration, filename, base_spectrum)
        results.append({
            'filename': filename,
            'concentration': concentration,
            'spectrum': spectrum
        })
    
    # Create summary file
    summary_file = "synthetic_data/dataset_summary.csv"
    with open(summary_file, 'w') as f:
        f.write("Filename,Target_Concentration_ppm\n")
        for result in results:
            f.write(f"{os.path.basename(result['filename'])},{result['concentration']:.1f}\n")
    
    print(f"\nGenerated {len(results)} synthetic datasets in '{output_dir}' directory")
    print(f"Concentration range: {min(concentrations):.1f} - {max(concentrations):.1f} ppm")
    print(f"Summary saved to: {summary_file}")
    
    return results

def create_sample_groups():
    """
    Create sample groups for batch processing (similar to real data structure)
    """
    
    # Create sample groups with multiple spectra per sample
    sample_groups = []
    
    # Group 1: Low concentration samples (0-50 ppm)
    for i in range(5):
        sample_name = f"Low_Pb_Sample_{i+1}"
        spectra_files = []
        for j in range(3):  # 3 spectra per sample
            concentration = np.random.uniform(0, 50)
            filename = f"synthetic_data/LOW_{i+1}_{j+1}_{concentration:.1f}ppm.txt"
            generate_synthetic_xrf_data(concentration, filename)
            spectra_files.append(filename)
        sample_groups.append((sample_name, spectra_files))
    
    # Group 2: Medium concentration samples (50-500 ppm)
    for i in range(5):
        sample_name = f"Medium_Pb_Sample_{i+1}"
        spectra_files = []
        for j in range(3):  # 3 spectra per sample
            concentration = np.random.uniform(50, 500)
            filename = f"synthetic_data/MED_{i+1}_{j+1}_{concentration:.1f}ppm.txt"
            generate_synthetic_xrf_data(concentration, filename)
            spectra_files.append(filename)
        sample_groups.append((sample_name, spectra_files))
    
    # Group 3: High concentration samples (500-2000 ppm)
    for i in range(5):
        sample_name = f"High_Pb_Sample_{i+1}"
        spectra_files = []
        for j in range(3):  # 3 spectra per sample
            concentration = np.random.uniform(500, 2000)
            filename = f"synthetic_data/HIGH_{i+1}_{j+1}_{concentration:.1f}ppm.txt"
            generate_synthetic_xrf_data(concentration, filename)
            spectra_files.append(filename)
        sample_groups.append((sample_name, spectra_files))
    
    # Create sample groups summary
    with open("synthetic_data/sample_groups_summary.csv", 'w') as f:
        f.write("Sample_Name,Spectrum_File,Target_Concentration_ppm\n")
        for sample_name, spectra_files in sample_groups:
            for spectrum_file in spectra_files:
                # Extract concentration from filename
                concentration = float(spectrum_file.split('_')[-1].replace('ppm.txt', ''))
                f.write(f"{sample_name},{os.path.basename(spectrum_file)},{concentration:.1f}\n")
    
    print(f"Created {len(sample_groups)} sample groups with multiple spectra each")
    print("Sample groups summary saved to: synthetic_data/sample_groups_summary.csv")
    
    return sample_groups

if __name__ == "__main__":
    print("XRF Synthetic Data Generator")
    print("=" * 40)
    
    # Generate individual datasets
    results = create_concentration_range_datasets()
    
    # Generate sample groups
    sample_groups = create_sample_groups()
    
    print("\nData generation complete!")
    print("You can now use these synthetic datasets to test your XRF analysis code.")
    print("The datasets include:")
    print("- 110 individual spectra with concentrations from 0 to 2000 ppm")
    print("- 15 sample groups (5 low, 5 medium, 5 high concentration) with 3 spectra each")
    print("- Realistic XRF background and Pb L-alpha peak structure")
    print("- Proper EMSA format matching your real data files") 