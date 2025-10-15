"""
XRF Fundamental Parameters (FP) Method Implementation

This module implements a quantitative XRF analysis approach based on 
fundamental parameters using the Sherman equation and xraylib for 
atomic data (cross-sections, fluorescence yields, etc.).

References:
- Sherman, J. (1955). "The theoretical derivation of fluorescent X-ray intensities from mixtures"
- xraylib: https://github.com/tschoonj/xraylib
- PyMca FP implementation: https://github.com/vasole/pymca
"""

import numpy as np
from scipy.optimize import minimize, least_squares
from typing import Dict, List, Tuple, Optional
import warnings

# Try to import xraylib (optional dependency)
try:
    import xraylib as xrl
    HAS_XRAYLIB = True
except ImportError:
    HAS_XRAYLIB = False
    warnings.warn("xraylib not found. Install with: pip install xraylib")


class XRFFundamentalParameters:
    """
    Fundamental Parameters method for quantitative XRF analysis.
    
    This class implements the Sherman equation to calculate theoretical
    X-ray fluorescence intensities and performs iterative fitting to
    determine elemental concentrations.
    """
    
    def __init__(self, tube_voltage: float = 50.0, tube_current: float = 1.0,
                 tube_element: str = 'Rh', detector_angle: float = 45.0,
                 takeoff_angle: float = 45.0):
        """
        Initialize FP calculator.
        
        Parameters:
        -----------
        tube_voltage : float
            X-ray tube voltage in kV
        tube_current : float
            X-ray tube current in mA
        tube_element : str
            X-ray tube anode element (e.g., 'Rh', 'W', 'Mo')
        detector_angle : float
            Detector angle relative to sample surface (degrees)
        takeoff_angle : float
            X-ray takeoff angle (degrees)
        """
        if not HAS_XRAYLIB:
            raise ImportError("xraylib is required for FP method. Install with: pip install xraylib")
        
        self.tube_voltage = tube_voltage  # kV
        self.tube_current = tube_current  # mA
        self.tube_element = tube_element
        self.detector_angle = np.radians(detector_angle)
        self.takeoff_angle = np.radians(takeoff_angle)
        
        # Physical constants
        self.AVOGADRO = 6.022e23  # mol^-1
        self.KEV_TO_ANGSTROM = 12.398  # keV to Angstrom conversion
        
    def get_tube_spectrum(self, energy_range: np.ndarray) -> np.ndarray:
        """
        Calculate X-ray tube spectrum (bremsstrahlung + characteristic lines).
        
        Parameters:
        -----------
        energy_range : np.ndarray
            Energy values in keV
            
        Returns:
        --------
        np.ndarray
            Relative intensity at each energy
        """
        intensities = np.zeros_like(energy_range)
        
        # Bremsstrahlung (Kramers' law approximation)
        mask = energy_range < self.tube_voltage
        Z_tube = xrl.SymbolToAtomicNumber(self.tube_element)
        intensities[mask] = Z_tube * (self.tube_voltage - energy_range[mask]) / energy_range[mask]
        
        # Add characteristic lines from tube element
        try:
            # K-alpha lines
            ka1_energy = xrl.LineEnergy(Z_tube, xrl.KL3_LINE)
            ka2_energy = xrl.LineEnergy(Z_tube, xrl.KL2_LINE)
            
            if ka1_energy < self.tube_voltage:
                ka1_idx = np.argmin(np.abs(energy_range - ka1_energy))
                ka2_idx = np.argmin(np.abs(energy_range - ka2_energy))
                
                # Relative intensities
                intensities[ka1_idx] += 100 * Z_tube
                intensities[ka2_idx] += 50 * Z_tube
                
            # K-beta lines
            kb1_energy = xrl.LineEnergy(Z_tube, xrl.KM3_LINE)
            if kb1_energy < self.tube_voltage:
                kb1_idx = np.argmin(np.abs(energy_range - kb1_energy))
                intensities[kb1_idx] += 20 * Z_tube
                
        except:
            pass  # Element doesn't have these lines
        
        return intensities / np.max(intensities) if np.max(intensities) > 0 else intensities
    
    def mass_attenuation_coefficient(self, element: str, energy: float) -> float:
        """
        Get mass attenuation coefficient for element at given energy.
        
        Parameters:
        -----------
        element : str
            Element symbol
        energy : float
            Energy in keV
            
        Returns:
        --------
        float
            Mass attenuation coefficient in cm²/g
        """
        Z = xrl.SymbolToAtomicNumber(element)
        return xrl.CS_Total(Z, energy)
    
    def fluorescence_yield(self, element: str, line: str = 'KA') -> float:
        """
        Get fluorescence yield for element and line.
        
        Parameters:
        -----------
        element : str
            Element symbol
        line : str
            Line type ('KA', 'KB', 'LA', 'LB')
            
        Returns:
        --------
        float
            Fluorescence yield (0-1)
        """
        Z = xrl.SymbolToAtomicNumber(element)
        
        if line.startswith('K'):
            return xrl.FluorYield(Z, xrl.K_SHELL)
        elif line.startswith('L'):
            return xrl.FluorYield(Z, xrl.L3_SHELL)
        else:
            return 0.0
    
    def jump_ratio(self, element: str, shell: str = 'K') -> float:
        """
        Get absorption edge jump ratio.
        
        Parameters:
        -----------
        element : str
            Element symbol
        shell : str
            Shell ('K', 'L', 'M')
            
        Returns:
        --------
        float
            Jump ratio
        """
        Z = xrl.SymbolToAtomicNumber(element)
        
        if shell == 'K':
            return xrl.JumpFactor(Z, xrl.K_SHELL)
        elif shell == 'L':
            return xrl.JumpFactor(Z, xrl.L3_SHELL)
        else:
            return 1.0
    
    def line_energy(self, element: str, line: str = 'KA1') -> float:
        """
        Get characteristic line energy.
        
        Parameters:
        -----------
        element : str
            Element symbol
        line : str
            Line designation
            
        Returns:
        --------
        float
            Energy in keV
        """
        Z = xrl.SymbolToAtomicNumber(element)
        
        line_map = {
            'KA1': xrl.KL3_LINE,
            'KA2': xrl.KL2_LINE,
            'KB1': xrl.KM3_LINE,
            'LA1': xrl.L3M5_LINE,
            'LB1': xrl.L2M4_LINE,
        }
        
        xrl_line = line_map.get(line.upper(), xrl.KL3_LINE)
        
        try:
            return xrl.LineEnergy(Z, xrl_line)
        except:
            return 0.0
    
    def calculate_primary_intensity(self, element: str, concentration: float,
                                    matrix_composition: Dict[str, float],
                                    line: str = 'KA1') -> float:
        """
        Calculate primary fluorescence intensity using Sherman equation.
        
        Parameters:
        -----------
        element : str
            Element of interest
        concentration : float
            Mass fraction (0-1)
        matrix_composition : Dict[str, float]
            Dictionary of element: mass_fraction for all matrix elements
        line : str
            Characteristic line
            
        Returns:
        --------
        float
            Theoretical intensity (arbitrary units)
        """
        Z = xrl.SymbolToAtomicNumber(element)
        line_e = self.line_energy(element, line)
        
        if line_e == 0:
            return 0.0
        
        # Get absorption edge energy
        if line.startswith('K'):
            edge_energy = xrl.EdgeEnergy(Z, xrl.K_SHELL)
        elif line.startswith('L'):
            edge_energy = xrl.EdgeEnergy(Z, xrl.L3_SHELL)
        else:
            return 0.0
        
        # Integrate over tube spectrum
        energy_range = np.linspace(edge_energy, self.tube_voltage, 100)
        tube_spectrum = self.get_tube_spectrum(energy_range)
        
        intensity = 0.0
        
        for i, E_in in enumerate(energy_range):
            if E_in < edge_energy:
                continue
            
            # Photoelectric cross-section
            tau = xrl.CS_Photo(Z, E_in)
            
            # Mass attenuation coefficients
            mu_in = sum(matrix_composition[elem] * self.mass_attenuation_coefficient(elem, E_in) 
                       for elem in matrix_composition)
            mu_out = sum(matrix_composition[elem] * self.mass_attenuation_coefficient(elem, line_e) 
                        for elem in matrix_composition)
            
            # Geometric factors
            sin_psi1 = np.sin(self.takeoff_angle)
            sin_psi2 = np.sin(self.detector_angle)
            
            # Sherman equation term
            denom = (mu_in / sin_psi1) + (mu_out / sin_psi2)
            
            if denom > 0:
                intensity += tube_spectrum[i] * tau * concentration / denom
        
        # Apply fluorescence yield and jump ratio
        omega = self.fluorescence_yield(element, line[:2])
        r = self.jump_ratio(element, line[0])
        
        return intensity * omega * (r - 1) / r
    
    def fit_composition(self, measured_intensities: Dict[str, float],
                       initial_composition: Optional[Dict[str, float]] = None,
                       normalize: bool = True) -> Dict[str, float]:
        """
        Fit elemental composition using measured intensities.
        
        Parameters:
        -----------
        measured_intensities : Dict[str, float]
            Dictionary of element: measured_intensity
        initial_composition : Dict[str, float], optional
            Initial guess for composition
        normalize : bool
            Whether to normalize composition to sum to 1
            
        Returns:
        --------
        Dict[str, float]
            Fitted composition (mass fractions)
        """
        elements = list(measured_intensities.keys())
        n_elements = len(elements)
        
        # Initial guess
        if initial_composition is None:
            x0 = np.ones(n_elements) / n_elements
        else:
            x0 = np.array([initial_composition.get(elem, 0.1) for elem in elements])
        
        # Normalize initial guess
        if normalize:
            x0 = x0 / np.sum(x0)
        
        def objective(x):
            """Objective function: sum of squared residuals."""
            if normalize:
                x = x / np.sum(x)  # Ensure normalization
            
            composition = {elem: conc for elem, conc in zip(elements, x)}
            
            residuals = []
            for elem in elements:
                calc_intensity = self.calculate_primary_intensity(elem, composition[elem], composition)
                meas_intensity = measured_intensities[elem]
                
                if meas_intensity > 0:
                    residuals.append((calc_intensity - meas_intensity) / meas_intensity)
                else:
                    residuals.append(calc_intensity)
            
            return np.sum(np.array(residuals)**2)
        
        # Constraints: all concentrations >= 0
        bounds = [(0, 1) for _ in range(n_elements)]
        
        # Constraint: sum to 1 if normalizing
        constraints = []
        if normalize:
            constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")
        
        # Return fitted composition
        fitted_composition = {elem: conc for elem, conc in zip(elements, result.x)}
        
        if normalize:
            total = sum(fitted_composition.values())
            fitted_composition = {k: v/total for k, v in fitted_composition.items()}
        
        return fitted_composition
    
    def calculate_concentration_from_intensity(self, element: str, intensity: float,
                                              matrix_elements: List[str],
                                              matrix_concentrations: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate concentration from measured intensity using FP method.
        
        Parameters:
        -----------
        element : str
            Element of interest
        intensity : float
            Measured intensity
        matrix_elements : List[str]
            List of matrix elements
        matrix_concentrations : Dict[str, float], optional
            Known matrix concentrations
            
        Returns:
        --------
        float
            Concentration in mass fraction
        """
        # If matrix is unknown, assume uniform distribution
        if matrix_concentrations is None:
            n = len(matrix_elements) + 1  # +1 for element of interest
            matrix_concentrations = {elem: 1.0/n for elem in matrix_elements}
            matrix_concentrations[element] = 1.0/n
        
        # Iterative approach: adjust element concentration to match intensity
        def objective(conc):
            comp = matrix_concentrations.copy()
            comp[element] = conc[0]
            
            # Renormalize
            total = sum(comp.values())
            comp = {k: v/total for k, v in comp.items()}
            
            calc_intensity = self.calculate_primary_intensity(element, comp[element], comp)
            return (calc_intensity - intensity)**2
        
        result = minimize(objective, [0.1], bounds=[(0, 1)], method='L-BFGS-B')
        
        return result.x[0]


def test_fp_method():
    """Test the FP method with a simple example."""
    if not HAS_XRAYLIB:
        print("xraylib not installed. Install with: pip install xraylib")
        return
    
    # Initialize FP calculator
    fp = XRFFundamentalParameters(tube_voltage=50.0, tube_element='Rh')
    
    # Test: Calculate intensity for pure Pb
    print("Testing FP Method")
    print("=" * 50)
    
    # Pure lead
    composition = {'Pb': 1.0}
    intensity_pb = fp.calculate_primary_intensity('Pb', 1.0, composition, 'LA1')
    print(f"Pb L-alpha intensity (pure): {intensity_pb:.6f}")
    
    # Lead in soil matrix (10% Pb, 90% SiO2 approximation)
    composition = {'Pb': 0.1, 'Si': 0.42, 'O': 0.48}
    intensity_pb_matrix = fp.calculate_primary_intensity('Pb', 0.1, composition, 'LA1')
    print(f"Pb L-alpha intensity (10% in matrix): {intensity_pb_matrix:.6f}")
    print(f"Matrix absorption effect: {intensity_pb_matrix/intensity_pb:.2%}")
    
    # Test fitting
    print("\nTesting composition fitting:")
    measured = {'Pb': intensity_pb_matrix, 'Si': 0.5, 'O': 0.3}
    fitted = fp.fit_composition(measured)
    print("Fitted composition:")
    for elem, conc in fitted.items():
        print(f"  {elem}: {conc:.4f} ({conc*100:.2f}%)")


if __name__ == "__main__":
    test_fp_method()
