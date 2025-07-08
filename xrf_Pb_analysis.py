import sys
import os
import re
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QFileDialog, QLabel, QLineEdit,
                               QTextEdit, QProgressBar, QGridLayout, QGroupBox,
                               QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                               QTableWidget, QTableWidgetItem, QTabWidget,
                               QMessageBox, QSplitter, QScrollArea, QDialog,
                               QDialogButtonBox, QTextBrowser)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy import integrate
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# Import matplotlib configuration
try:
    from matplotlib_config import (
        configure_compact_ui, 
        CompactNavigationToolbar, 
        MiniNavigationToolbar,
        apply_theme,
        get_toolbar_class
    )
    # Apply compact configuration
    configure_compact_ui()
except ImportError:
    print("Warning: matplotlib_config.py not found, using default matplotlib settings")
    CompactNavigationToolbar = None
    MiniNavigationToolbar = None


class FileSortingDialog(QDialog):
    """Dialog for previewing and selecting file sorting options"""
    
    def __init__(self, file_paths, folder_path, parent=None):
        super().__init__(parent)
        self.file_paths = file_paths
        self.folder_path = folder_path
        self.sorted_files = []
        
        self.setWindowTitle("File Sorting Options")
        self.setGeometry(300, 200, 800, 600)
        self.setModal(True)
        
        self.init_ui()
        self.load_files()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Preview and select file sorting method:")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Extension filtering
        filter_group = QGroupBox("File Type Filter")
        filter_layout = QVBoxLayout(filter_group)
        
        # Extension checkboxes
        self.extension_checkboxes = {}
        common_extensions = ['.txt', '.csv', '.xlsx', '.dat', '.emsa', '.spc']
        
        # Get all unique extensions from the files
        all_extensions = set()
        for file_path in self.file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            if ext:
                all_extensions.add(ext)
        
        # Sort extensions for consistent display
        all_extensions = sorted(all_extensions)
        
        # Create checkboxes for each extension
        ext_layout = QHBoxLayout()
        for ext in all_extensions:
            checkbox = QCheckBox(ext)
            checkbox.setChecked(True)  # Default to checked
            checkbox.stateChanged.connect(self.update_preview)
            self.extension_checkboxes[ext] = checkbox
            ext_layout.addWidget(checkbox)
        
        filter_layout.addLayout(ext_layout)
        
        # Quick selection buttons
        quick_buttons = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_extensions)
        quick_buttons.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_extensions)
        quick_buttons.addWidget(deselect_all_btn)
        
        # Add common XRF extensions button
        xrf_only_btn = QPushButton("XRF Files Only")
        xrf_only_btn.clicked.connect(self.select_xrf_extensions)
        quick_buttons.addWidget(xrf_only_btn)
        
        quick_buttons.addStretch()
        filter_layout.addLayout(quick_buttons)
        
        layout.addWidget(filter_group)
        
        # Sorting options
        options_group = QGroupBox("Sorting Options")
        options_layout = QHBoxLayout(options_group)
        
        self.sort_method_combo = QComboBox()
        self.sort_method_combo.addItems([
            "Smart Sort (Recommended)",
            "Alphabetical Sort",
            "Date Modified",
            "File Size",
            "Custom Order"
        ])
        self.sort_method_combo.currentTextChanged.connect(self.update_preview)
        options_layout.addWidget(QLabel("Sort Method:"))
        options_layout.addWidget(self.sort_method_combo)
        
        # Pattern detection
        self.pattern_label = QLabel("Detected Pattern: Unknown")
        self.pattern_label.setStyleSheet("color: #666; font-style: italic;")
        options_layout.addWidget(self.pattern_label)
        
        layout.addWidget(options_group)
        
        # Preview area
        preview_group = QGroupBox("File Order Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # File list
        self.file_list = QTableWidget()
        self.file_list.setColumnCount(3)
        self.file_list.setHorizontalHeaderLabels(["Order", "Filename", "Full Path"])
        self.file_list.horizontalHeader().setStretchLastSection(True)
        self.file_list.setAlternatingRowColors(True)
        preview_layout.addWidget(self.file_list)
        
        # Preview info
        self.preview_info = QLabel("Ready to preview files...")
        preview_layout.addWidget(self.preview_info)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Preview")
        self.refresh_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.accept_btn = QPushButton("Use This Order")
        self.accept_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.accept_btn)
        
        layout.addLayout(button_layout)
    
    def load_files(self):
        """Load and display files"""
        self.update_preview()
    
    def update_preview(self):
        """Update the file preview based on selected sorting method and extension filter"""
        # First filter by selected extensions
        selected_extensions = [ext for ext, checkbox in self.extension_checkboxes.items() 
                             if checkbox.isChecked()]
        
        if not selected_extensions:
            # If no extensions selected, show no files
            self.sorted_files = []
            self.pattern_label.setText("No file types selected")
            self.display_files()
            return
        
        # Filter files by selected extensions
        filtered_files = [f for f in self.file_paths 
                         if os.path.splitext(f)[1].lower() in selected_extensions]
        
        if not filtered_files:
            self.sorted_files = []
            self.pattern_label.setText("No files match selected extensions")
            self.display_files()
            return
        
        # Apply sorting method
        method = self.sort_method_combo.currentText()
        
        if method == "Smart Sort (Recommended)":
            self.sorted_files = self.smart_sort_files(filtered_files)
            pattern = self.detect_sorting_pattern(filtered_files)
            self.pattern_label.setText(f"Detected Pattern: {pattern}")
        elif method == "Alphabetical Sort":
            self.sorted_files = sorted(filtered_files)
            self.pattern_label.setText("Detected Pattern: Alphabetical")
        elif method == "Date Modified":
            self.sorted_files = sorted(filtered_files, key=lambda x: os.path.getmtime(x))
            self.pattern_label.setText("Detected Pattern: Date Modified")
        elif method == "File Size":
            self.sorted_files = sorted(filtered_files, key=lambda x: os.path.getsize(x))
            self.pattern_label.setText("Detected Pattern: File Size")
        elif method == "Custom Order":
            # For custom order, we'll keep the original order but allow manual reordering
            self.sorted_files = filtered_files.copy()
            self.pattern_label.setText("Detected Pattern: Custom")
        
        self.display_files()
    
    def smart_sort_files(self, file_paths):
        """Sort files using natural sorting (handles numbers correctly)"""
        def natural_sort_key(filename):
            basename = os.path.basename(filename)
            def convert(text):
                return int(text) if text.isdigit() else text.lower()
            return [convert(c) for c in re.split('([0-9]+)', basename)]
        
        return sorted(file_paths, key=natural_sort_key)
    
    def detect_sorting_pattern(self, file_paths):
        """Detect the naming pattern in the files"""
        if not file_paths:
            return "unknown"
        
        filenames = [os.path.basename(f) for f in file_paths]
        
        patterns = {
            "sample_number": r"sample_(\d+)",
            "sample_number_extended": r"sample_(\d+)_",
            "number_only": r"^(\d+)",
            "letter_number": r"([A-Za-z]+)(\d+)",
            "date_pattern": r"(\d{4})[-_](\d{2})[-_](\d{2})",
            "time_pattern": r"(\d{2})[-:](\d{2})[-:](\d{2})"
        }
        
        for pattern_name, pattern in patterns.items():
            matches = [re.search(pattern, f) for f in filenames]
            if all(matches):
                return pattern_name
        
        return "unknown"
    
    def display_files(self):
        """Display files in the table"""
        self.file_list.setRowCount(len(self.sorted_files))
        
        for i, file_path in enumerate(self.sorted_files):
            # Order number
            order_item = QTableWidgetItem(str(i + 1))
            order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.file_list.setItem(i, 0, order_item)
            
            # Filename
            filename_item = QTableWidgetItem(os.path.basename(file_path))
            self.file_list.setItem(i, 1, filename_item)
            
            # Full path
            path_item = QTableWidgetItem(file_path)
            path_item.setToolTip(file_path)
            self.file_list.setItem(i, 2, path_item)
        
        # Update info
        self.preview_info.setText(f"Showing {len(self.sorted_files)} files in {self.sort_method_combo.currentText()} order")
        
        # Resize columns
        self.file_list.resizeColumnsToContents()
    
    def get_sorted_files(self):
        """Return the sorted file list"""
        return self.sorted_files
    
    def select_all_extensions(self):
        """Select all file extensions"""
        for checkbox in self.extension_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_extensions(self):
        """Deselect all file extensions"""
        for checkbox in self.extension_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_xrf_extensions(self):
        """Select only common XRF file extensions"""
        xrf_extensions = ['.txt', '.csv', '.dat', '.emsa', '.spc']
        for ext, checkbox in self.extension_checkboxes.items():
            checkbox.setChecked(ext in xrf_extensions)


class XRFPeakFitter:
    """Core class for XRF peak fitting with background subtraction and Gaussian-A fitting"""
    
    def __init__(self):
        self.target_energy = 10.5  # Pb L-alpha peak at 10.5 keV
        # NIST calibration parameters
        self.calibration_slope = 13.8913
        self.calibration_intercept = 0.0
        
    def gaussian_a(self, x, a, x0, dx):
        """
        Gaussian-A function with the specified equation:
        sqrt(ln(2)/pi) * (a/dx) * exp(-ln(2) * (x-x0)^2 / dx^2)
        
        Parameters:
        - a: amplitude parameter
        - x0: peak center
        - dx: full width at half maximum (FWHM)
        """
        ln2 = np.log(2)
        coefficient = np.sqrt(ln2 / np.pi)
        amplitude = a / dx
        exponent = -ln2 * ((x - x0) ** 2) / (dx ** 2)
        return coefficient * amplitude * np.exp(exponent)
    
    def linear_background(self, x, m, b):
        """Linear background function"""
        return m * x + b
    
    def combined_model(self, x, a, x0, dx, m, b):
        """Combined peak + background model"""
        return self.gaussian_a(x, a, x0, dx) + self.linear_background(x, m, b)
    
    def estimate_background(self, x, y, peak_region):
        """Estimate linear background excluding peak region"""
        mask = ~((x >= peak_region[0]) & (x <= peak_region[1]))
        x_bg = x[mask]
        y_bg = y[mask]
        
        if len(x_bg) < 2:
            return 0, np.mean(y)
        
        # Linear fit to background points
        p = np.polyfit(x_bg, y_bg, 1)
        return p[0], p[1]
    
    def calculate_integrated_intensity(self, x, y, fit_params, peak_region):
        """
        Calculate integrated intensity of the peak after background subtraction
        
        Parameters:
        - x: energy array
        - y: intensity array
        - fit_params: fitted parameters
        - peak_region: integration region
        
        Returns:
        - integrated_intensity: background-corrected integrated peak area
        """
        # Select integration region
        mask = (x >= peak_region[0]) & (x <= peak_region[1])
        x_int = x[mask]
        y_int = y[mask]
        
        # Calculate background in integration region
        background = self.linear_background(x_int, 
                                          fit_params['background_slope'], 
                                          fit_params['background_intercept'])
        
        # Background-corrected intensity
        y_corrected = y_int - background
        
        # Integrate using trapezoidal rule
        integrated_intensity = integrate.trapz(y_corrected, x_int)
        
        return integrated_intensity
    
    def apply_calibration(self, integrated_intensity):
        """
        Apply NIST calibration curve to convert integrated intensity to concentration
        
        Calibration equation: Concentration = 13.8913 * AVE_I + 0
        
        Parameters:
        - integrated_intensity: background-corrected integrated peak area
        
        Returns:
        - concentration: calibrated concentration value
        """
        concentration = self.calibration_slope * integrated_intensity + self.calibration_intercept
        return concentration
    
    def fit_peak(self, x, y, peak_region=None, background_subtract=True, integration_region=None):
        """
        Fit Gaussian-A peak with optional background subtraction and calculate integrated intensity
        
        Parameters:
        - x: energy array
        - y: intensity array
        - peak_region: tuple (min_energy, max_energy) for fitting region
        - background_subtract: whether to include background in fit
        - integration_region: tuple (min_energy, max_energy) for integration
        
        Returns:
        - fit_params: dictionary with fit parameters
        - fit_curve: fitted curve
        - r_squared: coefficient of determination
        - integrated_intensity: background-corrected integrated peak area
        - concentration: calibrated concentration
        """
        if peak_region is None:
            peak_region = (self.target_energy - 0.5, self.target_energy + 0.5)
        
        if integration_region is None:
            integration_region = peak_region
        
        # Select fitting region
        mask = (x >= peak_region[0]) & (x <= peak_region[1])
        x_fit = x[mask]
        y_fit = y[mask]
        
        if len(x_fit) < 5:
            raise ValueError("Insufficient data points in fitting region")
        
        # Initial parameter estimation
        peak_idx = np.argmax(y_fit)
        x0_init = x_fit[peak_idx]
        a_init = np.max(y_fit)
        dx_init = 0.1  # Initial FWHM estimate
        
        try:
            if background_subtract:
                # Estimate background
                m_init, b_init = self.estimate_background(x_fit, y_fit, peak_region)
                
                # Initial guess
                p0 = [a_init, x0_init, dx_init, m_init, b_init]
                
                # Bounds for parameters [a, x0, dx, m, b]
                bounds = ([0, peak_region[0], 0.01, -np.inf, 0],
                         [np.inf, peak_region[1], 1.0, np.inf, np.inf])
                
                # Fit combined model
                popt, pcov = curve_fit(self.combined_model, x_fit, y_fit, p0=p0, bounds=bounds)
                
                # Calculate fitted curve
                fit_curve = self.combined_model(x_fit, *popt)
                
                # Extract parameters
                fit_params = {
                    'amplitude': popt[0],
                    'center': popt[1],
                    'fwhm': popt[2],
                    'background_slope': popt[3],
                    'background_intercept': popt[4],
                    'actual_peak_area': popt[0] * popt[2] * np.sqrt(np.pi / np.log(2)),  # Proper Gaussian-A area
                    'amplitude_error': np.sqrt(pcov[0,0]),
                    'center_error': np.sqrt(pcov[1,1]),
                    'fwhm_error': np.sqrt(pcov[2,2])
                }
                
            else:
                # Subtract estimated background first
                m_bg, b_bg = self.estimate_background(x_fit, y_fit, peak_region)
                y_bg_sub = y_fit - self.linear_background(x_fit, m_bg, b_bg)
                
                # Initial guess for peak only
                p0 = [a_init, x0_init, dx_init]
                
                # Bounds for parameters [a, x0, dx]
                bounds = ([0, peak_region[0], 0.01],
                         [np.inf, peak_region[1], 1.0])
                
                # Fit peak only
                popt, pcov = curve_fit(self.gaussian_a, x_fit, y_bg_sub, p0=p0, bounds=bounds)
                
                # Calculate fitted curve
                fit_curve = self.gaussian_a(x_fit, *popt) + self.linear_background(x_fit, m_bg, b_bg)
                
                # Extract parameters
                fit_params = {
                    'amplitude': popt[0],
                    'center': popt[1],
                    'fwhm': popt[2],
                    'background_slope': m_bg,
                    'background_intercept': b_bg,
                    'actual_peak_area': popt[0] * popt[2] * np.sqrt(np.pi / np.log(2)),  # Proper Gaussian-A area
                    'amplitude_error': np.sqrt(pcov[0,0]),
                    'center_error': np.sqrt(pcov[1,1]),
                    'fwhm_error': np.sqrt(pcov[2,2])
                }
            
            # Calculate R-squared
            ss_res = np.sum((y_fit - fit_curve) ** 2)
            ss_tot = np.sum((y_fit - np.mean(y_fit)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            
            # Calculate integrated intensity
            integrated_intensity = self.calculate_integrated_intensity(x, y, fit_params, integration_region)
            
            # Apply calibration
            concentration = self.apply_calibration(integrated_intensity)
            
            return fit_params, fit_curve, r_squared, x_fit, integrated_intensity, concentration
            
        except Exception as e:
            raise RuntimeError(f"Fitting failed: {str(e)}")

class SampleGroup:
    """Class to handle groups of spectra from the same sample"""
    
    def __init__(self, sample_name, spectra_data):
        self.sample_name = sample_name
        self.spectra_data = spectra_data  # List of (filename, fit_params, integrated_intensity, concentration)
        self.calculate_statistics()
    
    def calculate_statistics(self):
        """Calculate statistical parameters for the sample group"""
        if not self.spectra_data:
            return
        
        # Extract values
        integrated_intensities = [data[2] for data in self.spectra_data]
        concentrations = [data[3] for data in self.spectra_data]
        
        # Calculate statistics
        self.n_spectra = len(integrated_intensities)
        self.mean_integrated_intensity = np.mean(integrated_intensities)
        self.std_integrated_intensity = np.std(integrated_intensities, ddof=1) if len(integrated_intensities) > 1 else 0
        self.mean_concentration = np.mean(concentrations)
        self.std_concentration = np.std(concentrations, ddof=1) if len(concentrations) > 1 else 0
        
        # Calculate relative standard deviation (RSD)
        self.rsd_integrated_intensity = (self.std_integrated_intensity / self.mean_integrated_intensity * 100) if self.mean_integrated_intensity != 0 else 0
        self.rsd_concentration = (self.std_concentration / self.mean_concentration * 100) if self.mean_concentration != 0 else 0
        
        # Standard error of the mean
        self.sem_integrated_intensity = self.std_integrated_intensity / np.sqrt(self.n_spectra) if self.n_spectra > 0 else 0
        self.sem_concentration = self.std_concentration / np.sqrt(self.n_spectra) if self.n_spectra > 0 else 0

class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for displaying XRF spectra and fits"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 8))
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Apply compact theme
        try:
            apply_theme('compact')
        except:
            pass
        
    def setup_subplots(self):
        """Setup subplots for spectrum and calibration"""
        self.fig.clear()
        
        # Main spectrum plot
        self.ax1 = self.fig.add_subplot(2, 2, (1, 2))
        self.ax1.set_xlabel('Energy (keV)')
        self.ax1.set_ylabel('Intensity (counts)')
        self.ax1.grid(True, alpha=0.3)
        
        # Sample statistics plot
        self.ax2 = self.fig.add_subplot(2, 2, 3)
        self.ax2.set_xlabel('Sample Number')
        self.ax2.set_ylabel('Concentration')
        self.ax2.grid(True, alpha=0.3)
        
        # Calibration verification plot
        self.ax3 = self.fig.add_subplot(2, 2, 4)
        self.ax3.set_xlabel('Integrated Intensity')
        self.ax3.set_ylabel('Concentration')
        self.ax3.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        
    def plot_spectrum(self, x, y, fit_x=None, fit_y=None, background_x=None, background_y=None, 
                     r_squared=None, concentration=None, title="XRF Spectrum"):
        """Plot spectrum with optional fit overlay, background curve, R² value, and Pb concentration"""
        # Clear only the top subplot (ax1) for spectrum display
        self.ax1.clear()
        
        # Plot raw data
        self.ax1.plot(x, y, 'b-', linewidth=1, label='Raw Data', alpha=0.7)
        
        # Plot background curve if provided
        if background_x is not None and background_y is not None:
            self.ax1.plot(background_x, background_y, 'g--', linewidth=1.5, 
                         label='Background', alpha=0.8)
        
        # Plot fit if provided
        if fit_x is not None and fit_y is not None:
            self.ax1.plot(fit_x, fit_y, 'r-', linewidth=2, label='Gaussian-A Fit')
        
        self.ax1.set_xlabel('Energy (keV)')
        self.ax1.set_ylabel('Intensity (counts)')
        
        # Add R² to title if provided
        if r_squared is not None:
            title_with_r2 = f"{title} (R² = {r_squared:.4f})"
        else:
            title_with_r2 = title
        self.ax1.set_title(title_with_r2)
        
        self.ax1.grid(True, alpha=0.3)
        
        # Create legend with concentration info if available
        if concentration is not None:
            # Add concentration info to the plot
            legend_text = f'Pb: {concentration:.2f} ppm'
            self.ax1.text(0.02, 0.98, legend_text, transform=self.ax1.transAxes, 
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                         fontsize=10, fontweight='bold')
        
        self.ax1.legend()
        
        # Highlight Pb peak region
        self.ax1.axvspan(10.0, 11.0, alpha=0.2, color='yellow', label='Pb Peak Region')
        
        # Set zoom limits if available
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            self.ax1.set_xlim(self.display_min, self.display_max)
        else:
            # Default zoom around Pb peak if no custom range set
            self.ax1.set_xlim(9.5, 11.5)
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_sample_statistics(self, sample_groups):
        """Plot sample statistics and calibration verification"""
        if not sample_groups:
            return
        
        # Clear only the bottom subplots (ax2 and ax3) for statistics
        self.ax2.clear()
        self.ax3.clear()
        
        # Extract data for plotting
        sample_names = [group.sample_name for group in sample_groups]
        mean_concentrations = [group.mean_concentration for group in sample_groups]
        std_concentrations = [group.std_concentration for group in sample_groups]
        mean_intensities = [group.mean_integrated_intensity for group in sample_groups]
        
        # Sample statistics plot (NO error bars)
        x_pos = range(len(sample_names))
        self.ax2.plot(x_pos, mean_concentrations, 'o-', linewidth=2, markersize=6)
        self.ax2.set_xlabel('Sample Number')
        self.ax2.set_ylabel('Pb Concentration')
        self.ax2.set_title('Sample Concentrations')
        self.ax2.set_xticks(x_pos)
        self.ax2.set_xticklabels([f'S{i+1}' for i in x_pos])
        self.ax2.grid(True, alpha=0.3)

        # --- Dynamic x-axis label management ---
        num_labels = len(sample_names)
        if num_labels > 20:
            # Show every Nth label only
            N = max(1, num_labels // 20)
            for i, label in enumerate(self.ax2.get_xticklabels()):
                label.set_visible(i % N == 0)
            # Rotate and align
            import matplotlib.pyplot as plt
            plt.setp(self.ax2.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        else:
            import matplotlib.pyplot as plt
            plt.setp(self.ax2.get_xticklabels(), rotation=0, ha='center', fontsize=10)
        # --------------------------------------
        
        # Calibration verification plot
        self.ax3.scatter(mean_intensities, mean_concentrations, s=60, alpha=0.7, color='blue')
        
        # Plot calibration line
        if mean_intensities:
            x_cal = np.linspace(min(mean_intensities), max(mean_intensities), 100)
            y_cal = 13.8913 * x_cal + 0.0
            self.ax3.plot(x_cal, y_cal, 'r--', linewidth=2, label='NIST Calibration')
            self.ax3.legend()
        
        self.ax3.set_xlabel('Mean Integrated Intensity')
        self.ax3.set_ylabel('Mean Concentration')
        self.ax3.set_title('Calibration Verification')
        self.ax3.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()

class ProcessingThread(QThread):
    """Thread for batch processing XRF files with sample grouping"""
    
    progress = Signal(int)
    error_occurred = Signal(str, str)
    finished = Signal(list, list)
    
    def __init__(self, file_paths, fitting_params, spectra_per_sample):
        super().__init__()
        self.file_paths = file_paths
        self.fitting_params = fitting_params
        self.spectra_per_sample = spectra_per_sample
        self.fitter = XRFPeakFitter()
        
    def run(self):
        """Process all files in the list with sample grouping"""
        results = []
        sample_groups = []
        
        try:
            for i, file_path in enumerate(self.file_paths):
                try:
                    # Read XRF data
                    data = self.read_xrf_file(file_path)
                    
                    if data is None:
                        self.error_occurred.emit(file_path, "Could not read file")
                        continue
                    
                    x, y = data
                    
                    # Fit peak
                    fit_params, fit_curve, r_squared, x_fit, integrated_intensity, concentration = self.fitter.fit_peak(
                        x, y, 
                        peak_region=(self.fitting_params['peak_min'], self.fitting_params['peak_max']),
                        background_subtract=self.fitting_params['background_subtract'],
                        integration_region=(self.fitting_params['integration_min'], self.fitting_params['integration_max'])
                    )
                    
                    # Store results
                    result = {
                        'filename': os.path.basename(file_path),
                        'filepath': file_path,
                        'fit_params': fit_params,
                        'r_squared': r_squared,
                        'integrated_intensity': integrated_intensity,
                        'concentration': concentration,
                        'x_data': x,
                        'y_data': y,
                        'fit_x': x_fit,
                        'fit_y': fit_curve
                    }
                    
                    results.append(result)
                    
                    # Emit progress
                    progress_value = min(98, int((i + 1) / len(self.file_paths) * 98))  # Cap at 98% during file processing
                    self.progress.emit(progress_value)
                    
                except Exception as e:
                    self.error_occurred.emit(file_path, str(e))
                    # Still emit progress even for failed files
                    progress_value = min(98, int((i + 1) / len(self.file_paths) * 98))
                    self.progress.emit(progress_value)
            
            # Group results by sample (this can take some time)
            self.progress.emit(99)  # Show 99% while grouping
            sample_groups = self.group_by_sample(results)
            
            # Emit finished signal (100% will be set in on_batch_finished)
            self.finished.emit(results, sample_groups)
            
        except Exception as e:
            # Handle any unexpected errors in the thread
            self.error_occurred.emit("THREAD_ERROR", f"Unexpected error in processing thread: {str(e)}")
            self.finished.emit(results, sample_groups)  # Still emit finished to reset UI
    
    def group_by_sample(self, results):
        """Group results by sample based on spectra_per_sample"""
        sample_groups = []
        
        for i in range(0, len(results), self.spectra_per_sample):
            sample_data = []
            sample_number = (i // self.spectra_per_sample) + 1
            sample_name = f"Sample_{sample_number}"
            
            # Get spectra for this sample
            for j in range(i, min(i + self.spectra_per_sample, len(results))):
                result = results[j]
                sample_data.append((
                    result['filename'],
                    result['fit_params'],
                    result['integrated_intensity'],
                    result['concentration']
                ))
            
            if sample_data:
                sample_group = SampleGroup(sample_name, sample_data)
                sample_groups.append(sample_group)
        
        return sample_groups
    
    def read_xrf_file(self, file_path):
        """Read XRF data from various file formats"""
        try:
            # First try to read as EMSA format
            if file_path.lower().endswith('.txt'):
                try:
                    metadata, spectrum_df = parse_emsa_file_pandas(file_path)
                    if spectrum_df is not None and len(spectrum_df) > 0:
                        x = spectrum_df['energy_kev'].values
                        y = spectrum_df['counts'].values
                        return x, y
                except Exception as emsa_error:
                    print(f"Not EMSA format, trying other formats: {emsa_error}")
            
            # Try different file formats
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.lower().endswith('.txt'):
                df = pd.read_csv(file_path, delimiter='\t')
            elif file_path.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                # Try to read as space-separated values
                df = pd.read_csv(file_path, delimiter=r'\s+')
            
            # Assume first column is energy, second is intensity
            if len(df.columns) >= 2:
                x = df.iloc[:, 0].values
                y = df.iloc[:, 1].values
                return x, y
            else:
                return None
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

class XRFPeakFittingGUI(QMainWindow):
    """Main GUI application for XRF peak fitting with calibration and sample grouping"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XRF Peak Fitting with NIST Calibration - Pb L-alpha at 10.5 keV")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize components
        self.fitter = XRFPeakFitter()
        self.current_data = None
        self.processing_thread = None
        self.batch_results = []
        self.sample_groups = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create tab widget for left panel
        self.tab_widget = QTabWidget()
        
        # Create main workflow tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Single file selection
        single_file_layout = QHBoxLayout()
        self.single_file_btn = QPushButton("Select Single File")
        self.single_file_btn.clicked.connect(self.select_single_file)
        self.single_file_label = QLabel("No file selected")
        single_file_layout.addWidget(self.single_file_btn)
        single_file_layout.addWidget(self.single_file_label)
        file_layout.addLayout(single_file_layout)
        
        # Batch file selection
        batch_file_layout = QHBoxLayout()
        self.batch_folder_btn = QPushButton("Select Folder for Batch Processing")
        self.batch_folder_btn.clicked.connect(self.select_batch_folder)
        self.batch_folder_label = QLabel("No folder selected")
        batch_file_layout.addWidget(self.batch_folder_btn)
        batch_file_layout.addWidget(self.batch_folder_label)
        file_layout.addLayout(batch_file_layout)
        
        main_tab_layout.addWidget(file_group)
        
        # Sample grouping parameters
        grouping_group = QGroupBox("Sample Grouping")
        grouping_layout = QGridLayout(grouping_group)
        
        grouping_layout.addWidget(QLabel("Spectra per Sample:"), 0, 0)
        self.spectra_per_sample_spin = QSpinBox()
        self.spectra_per_sample_spin.setRange(1, 20)
        self.spectra_per_sample_spin.setValue(6)
        grouping_layout.addWidget(self.spectra_per_sample_spin, 0, 1)
        
        main_tab_layout.addWidget(grouping_group)
        
        # Processing buttons
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout(process_group)
        
        self.fit_single_btn = QPushButton("Fit Single File")
        self.fit_single_btn.clicked.connect(self.fit_single_file)
        self.fit_single_btn.setEnabled(False)
        process_layout.addWidget(self.fit_single_btn)
        
        self.fit_batch_btn = QPushButton("Process Batch")
        self.fit_batch_btn.clicked.connect(self.process_batch)
        self.fit_batch_btn.setEnabled(False)
        process_layout.addWidget(self.fit_batch_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        process_layout.addWidget(self.progress_bar)
        
        main_tab_layout.addWidget(process_group)
        
        # Results display
        results_group = QGroupBox("Fit Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(250)
        self.results_text.setFont(QFont("Courier", 9))
        results_layout.addWidget(self.results_text)
        
        main_tab_layout.addWidget(results_group)
        

        

        
        # Spectrum Browser
        browser_group = QGroupBox("Spectrum Browser")
        browser_layout = QVBoxLayout(browser_group)
        
        # Browser controls
        browser_controls = QHBoxLayout()
        self.prev_spectrum_btn = QPushButton("◀ Previous")
        self.prev_spectrum_btn.clicked.connect(self.show_previous_spectrum)
        self.prev_spectrum_btn.setEnabled(False)
        browser_controls.addWidget(self.prev_spectrum_btn)
        
        self.spectrum_info_label = QLabel("No spectra available")
        self.spectrum_info_label.setAlignment(Qt.AlignCenter)
        browser_controls.addWidget(self.spectrum_info_label)
        
        self.next_spectrum_btn = QPushButton("Next ▶")
        self.next_spectrum_btn.clicked.connect(self.show_next_spectrum)
        self.next_spectrum_btn.setEnabled(False)
        browser_controls.addWidget(self.next_spectrum_btn)
        
        browser_layout.addLayout(browser_controls)
        
        # Quick navigation
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(QLabel("Go to:"))
        self.spectrum_spinbox = QSpinBox()
        self.spectrum_spinbox.setMinimum(1)
        self.spectrum_spinbox.setMaximum(1)
        self.spectrum_spinbox.valueChanged.connect(self.go_to_spectrum)
        nav_layout.addWidget(self.spectrum_spinbox)
        nav_layout.addWidget(QLabel("of"))
        self.total_spectra_label = QLabel("0")
        nav_layout.addWidget(self.total_spectra_label)
        nav_layout.addStretch()
        browser_layout.addLayout(nav_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by R²:"))
        self.r2_filter_spin = QDoubleSpinBox()
        self.r2_filter_spin.setRange(0.0, 1.0)
        self.r2_filter_spin.setValue(0.0)
        self.r2_filter_spin.setSingleStep(0.1)
        self.r2_filter_spin.setDecimals(3)
        self.r2_filter_spin.valueChanged.connect(self.apply_r2_filter)
        filter_layout.addWidget(self.r2_filter_spin)
        filter_layout.addWidget(QLabel("or higher"))
        filter_layout.addStretch()
        browser_layout.addLayout(filter_layout)
        
        main_tab_layout.addWidget(browser_group)
        
        # Plot controls removed - statistics now show automatically after batch processing
        
        # Add zoom controls for top plot
        zoom_group = QGroupBox("Top Plot Zoom (keV)")
        zoom_layout = QHBoxLayout(zoom_group)
        zoom_layout.addWidget(QLabel("Display Min (keV):"))
        self.display_min_spin = QDoubleSpinBox()
        self.display_min_spin.setRange(0.0, 20.0)
        self.display_min_spin.setValue(8.0)
        self.display_min_spin.setSingleStep(0.1)
        zoom_layout.addWidget(self.display_min_spin)
        zoom_layout.addWidget(QLabel("Display Max (keV):"))
        self.display_max_spin = QDoubleSpinBox()
        self.display_max_spin.setRange(0.0, 20.0)
        self.display_max_spin.setValue(13.0)
        self.display_max_spin.setSingleStep(0.1)
        zoom_layout.addWidget(self.display_max_spin)
        main_tab_layout.addWidget(zoom_group)
        # Connect zoom controls to update plot
        self.display_min_spin.valueChanged.connect(self.update_top_plot_zoom)
        self.display_max_spin.valueChanged.connect(self.update_top_plot_zoom)
        
        # Add stretch to push everything to top
        main_tab_layout.addStretch()
        
        # Initialize sorting-related attributes
        self.batch_file_paths = []
        self.sorted_file_paths = []
        
        # Create advanced parameters tab
        advanced_tab = QWidget()
        advanced_tab_layout = QVBoxLayout(advanced_tab)

        # Add a QTabWidget for subtabs in Advanced Parameters
        self.advanced_subtabs = QTabWidget()
        advanced_tab_layout.addWidget(self.advanced_subtabs)

        # Fitting parameters group (as first subtab)
        fitting_tab = QWidget()
        fitting_layout = QVBoxLayout(fitting_tab)
        params_group = QGroupBox("Fitting Parameters")
        params_layout = QGridLayout(params_group)
        
        # Peak region
        params_layout.addWidget(QLabel("Peak Min (keV):"), 0, 0)
        self.peak_min_spin = QDoubleSpinBox()
        self.peak_min_spin.setRange(8.0, 12.0)
        self.peak_min_spin.setValue(10.0)
        self.peak_min_spin.setSingleStep(0.1)
        self.peak_min_spin.setDecimals(2)
        params_layout.addWidget(self.peak_min_spin, 0, 1)
        
        params_layout.addWidget(QLabel("Peak Max (keV):"), 1, 0)
        self.peak_max_spin = QDoubleSpinBox()
        self.peak_max_spin.setRange(8.0, 12.0)
        self.peak_max_spin.setValue(11.0)
        self.peak_max_spin.setSingleStep(0.1)
        self.peak_max_spin.setDecimals(2)
        params_layout.addWidget(self.peak_max_spin, 1, 1)
        
        # Integration region
        params_layout.addWidget(QLabel("Integration Min (keV):"), 2, 0)
        self.integration_min_spin = QDoubleSpinBox()
        self.integration_min_spin.setRange(8.0, 12.0)
        self.integration_min_spin.setValue(9.8)
        self.integration_min_spin.setSingleStep(0.1)
        self.integration_min_spin.setDecimals(2)
        params_layout.addWidget(self.integration_min_spin, 2, 1)
        
        params_layout.addWidget(QLabel("Integration Max (keV):"), 3, 0)
        self.integration_max_spin = QDoubleSpinBox()
        self.integration_max_spin.setRange(8.0, 12.0)
        self.integration_max_spin.setValue(11.2)
        self.integration_max_spin.setSingleStep(0.1)
        self.integration_max_spin.setDecimals(2)
        params_layout.addWidget(self.integration_max_spin, 3, 1)
        
        # Background subtraction
        self.bg_subtract_check = QCheckBox("Include Background in Fit")
        self.bg_subtract_check.setChecked(True)
        params_layout.addWidget(self.bg_subtract_check, 4, 0, 1, 2)
        
        fitting_layout.addWidget(params_group)
        
        # Calibration parameters group
        calibration_group = QGroupBox("NIST Calibration Parameters")
        calibration_layout = QGridLayout(calibration_group)
        
        calibration_layout.addWidget(QLabel("Slope:"), 0, 0)
        self.calibration_slope_edit = QLineEdit("13.8913")
        self.calibration_slope_edit.setReadOnly(True)
        self.calibration_slope_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 3px;
                font-family: 'Courier', monospace;
            }
        """)
        calibration_layout.addWidget(self.calibration_slope_edit, 0, 1)
        
        calibration_layout.addWidget(QLabel("Intercept:"), 1, 0)
        self.calibration_intercept_edit = QLineEdit("0.0")
        self.calibration_intercept_edit.setReadOnly(True)
        self.calibration_intercept_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 3px;
                font-family: 'Courier', monospace;
            }
        """)
        calibration_layout.addWidget(self.calibration_intercept_edit, 1, 1)
        
        # Enable edit button
        self.edit_calibration_btn = QPushButton("🔓 Enable Edit Mode")
        self.edit_calibration_btn.clicked.connect(self.enable_calibration_edit)
        calibration_layout.addWidget(self.edit_calibration_btn, 2, 0, 1, 2)
        
        self.update_calibration_btn = QPushButton("Update Calibration")
        self.update_calibration_btn.setVisible(False)
        self.update_calibration_btn.clicked.connect(self.update_calibration)
        calibration_layout.addWidget(self.update_calibration_btn, 3, 0, 1, 2)
        
        fitting_layout.addWidget(calibration_group)
        fitting_layout.addStretch()
        self.advanced_subtabs.addTab(fitting_tab, "Fitting & Calibration")

        # Remove protocol subtab - will be replaced with button

        # Add stretch to push everything to top
        advanced_tab_layout.addStretch()
        
        # Create Docs/Export tab
        docs_export_tab = QWidget()
        docs_export_layout = QVBoxLayout(docs_export_tab)
        
        # Documentation section
        docs_group = QGroupBox("Documentation")
        docs_layout = QVBoxLayout(docs_group)
        
        self.view_protocol_btn = QPushButton("📋 View XRF SOP")
        self.view_protocol_btn.clicked.connect(self.show_protocol_dialog)
        docs_layout.addWidget(self.view_protocol_btn)
        
        docs_export_layout.addWidget(docs_group)
        
        # Export section
        export_group = QGroupBox("Export Results")
        export_layout = QVBoxLayout(export_group)
        
        self.export_individual_btn = QPushButton("Export Individual Results to CSV")
        self.export_individual_btn.clicked.connect(self.export_individual_results)
        self.export_individual_btn.setEnabled(False)
        export_layout.addWidget(self.export_individual_btn)
        
        self.export_samples_btn = QPushButton("Export Sample Statistics to CSV")
        self.export_samples_btn.clicked.connect(self.export_sample_statistics)
        self.export_samples_btn.setEnabled(False)
        export_layout.addWidget(self.export_samples_btn)
        
        docs_export_layout.addWidget(export_group)
        
        # Report Generation section
        report_group = QGroupBox("Report Generation")
        report_layout = QVBoxLayout(report_group)
        
        # Report options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Report Format:"))
        self.report_format_combo = QComboBox()
        self.report_format_combo.addItems(["PDF", "HTML"])  # Removed 'Word Document'
        options_layout.addWidget(self.report_format_combo)
        options_layout.addStretch()
        report_layout.addLayout(options_layout)
        
        # Report content options
        content_layout = QVBoxLayout()
        
        self.include_protocol_check = QCheckBox("Include Protocol Summary")
        self.include_protocol_check.setChecked(True)
        content_layout.addWidget(self.include_protocol_check)
        
        self.include_spectra_check = QCheckBox("Include Example Spectra Plots")
        self.include_spectra_check.setChecked(True)
        content_layout.addWidget(self.include_spectra_check)
        
        self.include_statistics_check = QCheckBox("Include Detailed Statistics Tables")
        self.include_statistics_check.setChecked(True)
        content_layout.addWidget(self.include_statistics_check)
        
        self.include_calibration_check = QCheckBox("Include Calibration Information")
        self.include_calibration_check.setChecked(True)
        content_layout.addWidget(self.include_calibration_check)
        
        report_layout.addLayout(content_layout)
        
        # Report generation buttons
        report_buttons_layout = QHBoxLayout()
        
        self.generate_all_reports_btn = QPushButton("📊 Generate All Sample Reports")
        self.generate_all_reports_btn.clicked.connect(self.generate_all_sample_reports)
        self.generate_all_reports_btn.setEnabled(False)
        report_buttons_layout.addWidget(self.generate_all_reports_btn)
        
        self.generate_single_report_btn = QPushButton("📋 Generate Single Report")
        self.generate_single_report_btn.clicked.connect(self.generate_single_sample_report)
        self.generate_single_report_btn.setEnabled(False)
        report_buttons_layout.addWidget(self.generate_single_report_btn)
        
        report_layout.addLayout(report_buttons_layout)
        
        docs_export_layout.addWidget(report_group)
        
        # Add stretch to push everything to top
        docs_export_layout.addStretch()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(main_tab, "Main Workflow")
        self.tab_widget.addTab(advanced_tab, "Advanced Parameters")
        self.tab_widget.addTab(docs_export_tab, "Docs / Export")
        
        # Create right panel for plot
        right_panel = QVBoxLayout()
        
        # Plot canvas with navigation toolbar
        self.plot_canvas = PlotCanvas()
        
        # Add navigation toolbar if available
        if CompactNavigationToolbar is not None:
            self.plot_toolbar = CompactNavigationToolbar(self.plot_canvas, self)
            right_panel.addWidget(self.plot_toolbar)
        else:
            # Fallback to standard toolbar
            from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
            self.plot_toolbar = NavigationToolbar2QT(self.plot_canvas, self)
            right_panel.addWidget(self.plot_toolbar)
        
        right_panel.addWidget(self.plot_canvas)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.tab_widget)
        left_widget.setMaximumWidth(450)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 1150])
        
        main_layout.addWidget(splitter)
        
    def enable_calibration_edit(self):
        """Enable edit mode for calibration parameters"""
        reply = QMessageBox.question(
            self, 
            "Enable Edit Mode", 
            "Are you sure you want to enable editing of NIST calibration parameters?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Enable editing
            self.calibration_slope_edit.setReadOnly(False)
            self.calibration_intercept_edit.setReadOnly(False)
            self.calibration_slope_edit.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 3px;
                    border-radius: 3px;
                    font-family: 'Courier', monospace;
                }
            """)
            self.calibration_intercept_edit.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 3px;
                    border-radius: 3px;
                    font-family: 'Courier', monospace;
                }
            """)
            
            # Show update button
            self.update_calibration_btn.setVisible(True)
            self.edit_calibration_btn.setText("🔒 Disable Edit Mode")
            self.edit_calibration_btn.clicked.disconnect()
            self.edit_calibration_btn.clicked.connect(self.disable_calibration_edit)
    
    def disable_calibration_edit(self):
        """Disable edit mode for calibration parameters"""
        # Disable editing
        self.calibration_slope_edit.setReadOnly(True)
        self.calibration_intercept_edit.setReadOnly(True)
        self.calibration_slope_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 3px;
                font-family: 'Courier', monospace;
            }
        """)
        self.calibration_intercept_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 3px;
                font-family: 'Courier', monospace;
            }
        """)
        
        # Hide update button
        self.update_calibration_btn.setVisible(False)
        self.edit_calibration_btn.setText("🔓 Enable Edit Mode")
        self.edit_calibration_btn.clicked.disconnect()
        self.edit_calibration_btn.clicked.connect(self.enable_calibration_edit)
    
    def update_calibration(self):
        """Update calibration parameters"""
        try:
            slope = float(self.calibration_slope_edit.text())
            intercept = float(self.calibration_intercept_edit.text())
            
            self.fitter.calibration_slope = slope
            self.fitter.calibration_intercept = intercept
            
            QMessageBox.information(self, "Calibration Updated", 
                                  f"Calibration updated:\nSlope: {slope}\nIntercept: {intercept}")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for calibration parameters")
        
    def select_single_file(self):
        """Select a single XRF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select XRF File", "", 
            "All Files (*);;CSV Files (*.csv);;Text Files (*.txt);;Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.single_file_label.setText(os.path.basename(file_path))
            self.current_file_path = file_path
            self.fit_single_btn.setEnabled(True)
            
            # Try to load and display the file
            self.load_and_display_file(file_path)
    
    def select_batch_folder(self):
        """Select folder for batch processing"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder with XRF Files")
        
        if folder_path:
            # Get all files in the folder first, then let user filter by extension
            all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                        if os.path.isfile(os.path.join(folder_path, f))]
            
            if all_files:
                # Show sorting dialog with extension filtering
                self.show_sorting_dialog(all_files, folder_path)
            else:
                self.batch_folder_label.setText("No files found")
                self.fit_batch_btn.setEnabled(False)
    
    def load_and_display_file(self, file_path):
        """Load and display XRF file"""
        try:
            # Read file
            data = self.read_xrf_file(file_path)
            if data is None:
                QMessageBox.warning(self, "Error", f"Could not read file: {file_path}")
                return
            
            x, y = data
            self.current_data = (x, y)
            
            # Display spectrum
            self.plot_canvas.plot_spectrum(x, y, title=f"XRF Spectrum - {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading file: {str(e)}")
    
    def read_xrf_file(self, file_path):
        """Read XRF data from file"""
        try:
            # First try to read as EMSA format
            if file_path.lower().endswith('.txt'):
                try:
                    metadata, spectrum_df = parse_emsa_file_pandas(file_path)
                    if spectrum_df is not None and len(spectrum_df) > 0:
                        x = spectrum_df['energy_kev'].values
                        y = spectrum_df['counts'].values
                        return x, y
                except Exception as emsa_error:
                    print(f"Not EMSA format, trying other formats: {emsa_error}")
            
            # Try other formats
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.lower().endswith('.txt') or file_path.lower().endswith('.dat'):
                df = pd.read_csv(file_path, delimiter='\t')
            elif file_path.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, delimiter=r'\s+')
            
            if len(df.columns) >= 2:
                x = df.iloc[:, 0].values
                y = df.iloc[:, 1].values
                return x, y
            else:
                return None
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def fit_single_file(self):
        """Fit peak for single file"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            QMessageBox.warning(self, "Error", "No data loaded")
            return
        
        try:
            x, y = self.current_data
            
            # Get fitting parameters
            peak_min = self.peak_min_spin.value()
            peak_max = self.peak_max_spin.value()
            integration_min = self.integration_min_spin.value()
            integration_max = self.integration_max_spin.value()
            background_subtract = self.bg_subtract_check.isChecked()
            
            # Perform fit
            fit_params, fit_curve, r_squared, x_fit, integrated_intensity, concentration = self.fitter.fit_peak(
                x, y, 
                peak_region=(peak_min, peak_max),
                background_subtract=background_subtract,
                integration_region=(integration_min, integration_max)
            )
            
            # Display results
            self.display_fit_results(fit_params, r_squared, integrated_intensity, concentration)
            
            # Calculate background curve for display
            background_x = None
            background_y = None
            if fit_params and 'background_slope' in fit_params and 'background_intercept' in fit_params:
                background_x = x_fit
                background_y = self.fitter.linear_background(x_fit, 
                                                           fit_params['background_slope'], 
                                                           fit_params['background_intercept'])
            
            # Update plot with background curve, R², and concentration
            # Ensure subplots are set up first if not already done
            if not hasattr(self.plot_canvas, 'ax1'):
                self.plot_canvas.setup_subplots()
            
            self.plot_canvas.plot_spectrum(
                x, y, 
                fit_x=x_fit, 
                fit_y=fit_curve,
                background_x=background_x,
                background_y=background_y,
                r_squared=r_squared,
                concentration=concentration,
                title=f"XRF Spectrum with Gaussian-A Fit - {os.path.basename(self.current_file_path)}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Fitting Error", f"Error during fitting: {str(e)}")
    
    def process_batch(self):
        """Process batch of files with sample grouping"""
        if not hasattr(self, 'batch_file_paths'):
            QMessageBox.warning(self, "Error", "No files selected for batch processing")
            return
        
        # Get fitting parameters
        fitting_params = {
            'peak_min': self.peak_min_spin.value(),
            'peak_max': self.peak_max_spin.value(),
            'integration_min': self.integration_min_spin.value(),
            'integration_max': self.integration_max_spin.value(),
            'background_subtract': self.bg_subtract_check.isChecked()
        }
        
        spectra_per_sample = self.spectra_per_sample_spin.value()
        
        # Start processing thread
        self.processing_thread = ProcessingThread(self.batch_file_paths, fitting_params, spectra_per_sample)
        self.processing_thread.progress.connect(self.progress_bar.setValue)
        self.processing_thread.error_occurred.connect(self.on_processing_error)
        self.processing_thread.finished.connect(self.on_batch_finished)
        
        # Disable buttons during processing
        self.fit_batch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Clear previous results and reset counters
        self.results_text.clear()
        self.files_processed_count = 0
        self.latest_processed_data = None
        
        # Initialize progress tracking
        self.total_files = len(self.batch_file_paths)
        
        # Start processing
        self.processing_thread.start()
    

    
    def on_processing_error(self, file_path, error_msg):
        """Handle processing error"""
        filename = os.path.basename(file_path)
        self.results_text.append(f"ERROR: {filename} - {error_msg}")
    
    def on_batch_finished(self, results, sample_groups):
        """Handle batch processing completion"""
        # Ensure progress bar reaches 100%
        self.progress_bar.setValue(100)
        
        self.batch_results = results
        self.sample_groups = sample_groups
        self.fit_batch_btn.setEnabled(True)
        self.export_individual_btn.setEnabled(True)
        self.export_samples_btn.setEnabled(True)
        self.generate_all_reports_btn.setEnabled(True)
        self.generate_single_report_btn.setEnabled(True)
        
        # Initialize spectrum browser
        self.initialize_spectrum_browser()
        
        # Display sample statistics
        self.display_sample_statistics(sample_groups)
        
        # Automatically show sample statistics plot
        if sample_groups:
            # Ensure subplots are set up first
            self.plot_canvas.setup_subplots()
            self.plot_canvas.plot_sample_statistics(sample_groups)
        
        # Display summary
        successful = len([r for r in results if 'fit_params' in r])
        total = len(self.batch_file_paths)
        
        self.results_text.append(f"\n=== BATCH PROCESSING COMPLETE ===")
        self.results_text.append(f"Total files processed: {successful}/{total}")
        self.results_text.append(f"Samples analyzed: {len(sample_groups)}")
        
        QMessageBox.information(self, "Batch Processing Complete", 
                              f"Processing complete!\n{successful}/{total} files processed successfully\n{len(sample_groups)} samples analyzed\n\nUse the Spectrum Browser to examine individual fits.")
    
    def display_fit_results(self, fit_params, r_squared, integrated_intensity, concentration):
        """Display fitting results for single file"""
        results_text = f"""
Gaussian-A Fit Results:
========================
Peak Center: {fit_params['center']:.4f} ± {fit_params['center_error']:.4f} keV
Amplitude: {fit_params['amplitude']:.2f} ± {fit_params['amplitude_error']:.2f}
FWHM: {fit_params['fwhm']:.4f} ± {fit_params['fwhm_error']:.4f} keV
Actual Peak Area: {fit_params['actual_peak_area']:.2f}
Background Slope: {fit_params['background_slope']:.4f}
Background Intercept: {fit_params['background_intercept']:.2f}
R-squared: {r_squared:.6f}

Quantitative Analysis:
=====================
Integrated Intensity: {integrated_intensity:.2f}
Calibrated Concentration: {concentration:.4f}
"""
        self.results_text.setText(results_text)
    
    def display_sample_statistics(self, sample_groups):
        """Display sample statistics in results text area"""
        self.results_text.append(f"\n=== SAMPLE STATISTICS ===")
        
        for group in sample_groups:
            self.results_text.append(f"\n{group.sample_name} (n={group.n_spectra}):")
            self.results_text.append(f"  Mean Intensity: {group.mean_integrated_intensity:.2f}")
            self.results_text.append(f"  Intensity SD: {group.std_integrated_intensity:.2f}")
            self.results_text.append(f"  Intensity SEM: {group.sem_integrated_intensity:.2f}")
            self.results_text.append(f"  Intensity RSD (%): {group.rsd_integrated_intensity:.2f}")
            self.results_text.append(f"  Mean Concentration: {group.mean_concentration:.4f}")
            self.results_text.append(f"  Concentration SD: {group.std_concentration:.4f}")
            self.results_text.append(f"  Concentration SEM: {group.sem_concentration:.4f}")
            self.results_text.append(f"  Concentration RSD (%): {group.rsd_concentration:.2f}")
    
    def export_individual_results(self):
        """Export individual spectrum results to CSV"""
        if not self.batch_results:
            QMessageBox.warning(self, "Error", "No batch results to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Individual Results", "xrf_individual_results.csv", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Prepare data for export
                export_data = []
                for i, result in enumerate(self.batch_results):
                    if 'fit_params' in result:
                        fp = result['fit_params']
                        sample_number = (i // self.spectra_per_sample_spin.value()) + 1
                        spectrum_number = (i % self.spectra_per_sample_spin.value()) + 1
                        
                        export_data.append({
                            'filename': result['filename'],
                            'sample_number': sample_number,
                            'spectrum_number': spectrum_number,
                            'peak_center_keV': fp['center'],
                            'peak_center_error_keV': fp['center_error'],
                            'amplitude': fp['amplitude'],
                            'amplitude_error': fp['amplitude_error'],
                            'fwhm_keV': fp['fwhm'],
                            'fwhm_error_keV': fp['fwhm_error'],
                            'actual_peak_area': fp['actual_peak_area'],
                            'background_slope': fp['background_slope'],
                            'background_intercept': fp['background_intercept'],
                            'r_squared': result['r_squared'],
                            'integrated_intensity': result['integrated_intensity'],
                            'concentration': result['concentration']
                        })
                
                # Create DataFrame and export
                df = pd.DataFrame(export_data)
                df.to_csv(file_path, index=False)
                
                QMessageBox.information(self, "Export Complete", f"Individual results exported to {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Error exporting results: {str(e)}")
    
    def export_sample_statistics(self):
        """Export sample statistics to CSV"""
        if not self.sample_groups:
            QMessageBox.warning(self, "Error", "No sample statistics to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Sample Statistics", "xrf_sample_statistics.csv", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Prepare data for export
                export_data = []
                for group in self.sample_groups:
                    export_data.append({
                        'sample_name': group.sample_name,
                        'n_spectra': group.n_spectra,
                        'mean_integrated_intensity': group.mean_integrated_intensity,
                        'std_integrated_intensity': group.std_integrated_intensity,
                        'rsd_integrated_intensity_percent': group.rsd_integrated_intensity,
                        'sem_integrated_intensity': group.sem_integrated_intensity,
                        'mean_concentration': group.mean_concentration,
                        'std_concentration': group.std_concentration,
                        'rsd_concentration_percent': group.rsd_concentration,
                        'sem_concentration': group.sem_concentration
                    })
                
                # Create DataFrame and export
                df = pd.DataFrame(export_data)
                df.to_csv(file_path, index=False)
                
                QMessageBox.information(self, "Export Complete", f"Sample statistics exported to {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Error exporting sample statistics: {str(e)}")

    def initialize_spectrum_browser(self):
        """Initialize the spectrum browser with processed results"""
        if not self.batch_results:
            return
        
        # Filter successful results
        self.filtered_results = [r for r in self.batch_results if 'fit_params' in r]
        
        if not self.filtered_results:
            return
        
        # Initialize browser state
        self.current_spectrum_index = 0
        self.total_spectra = len(self.filtered_results)
        
        # Update UI controls
        self.total_spectra_label.setText(str(self.total_spectra))
        self.spectrum_spinbox.setMaximum(self.total_spectra)
        self.spectrum_spinbox.setValue(1)
        
        # Enable browser controls
        self.prev_spectrum_btn.setEnabled(True)
        self.next_spectrum_btn.setEnabled(True)
        
        # Show first spectrum
        self.show_current_spectrum()
    
    def show_current_spectrum(self):
        """Display the current spectrum in the browser"""
        if not hasattr(self, 'filtered_results') or not self.filtered_results:
            return
        
        if self.current_spectrum_index >= len(self.filtered_results):
            return
        
        result = self.filtered_results[self.current_spectrum_index]
        
        # Extract data
        x = result['x_data']
        y = result['y_data']
        fit_x = result['fit_x']
        fit_y = result['fit_y']
        filename = result['filename']
        fit_params = result['fit_params']
        r_squared = result['r_squared']
        concentration = result['concentration']
        
        # Calculate background curve for display
        background_x = None
        background_y = None
        if fit_params and 'background_slope' in fit_params and 'background_intercept' in fit_params:
            # Use the same x range as the fit for background display
            if fit_x is not None:
                background_x = fit_x
                background_y = self.fitter.linear_background(fit_x, 
                                                           fit_params['background_slope'], 
                                                           fit_params['background_intercept'])
        
        # Update plot with background curve, R², and concentration
        # Ensure subplots are set up first if not already done
        if not hasattr(self.plot_canvas, 'ax1'):
            self.plot_canvas.setup_subplots()
        
        self.plot_canvas.plot_spectrum(
            x, y, 
            fit_x=fit_x, 
            fit_y=fit_y,
            background_x=background_x,
            background_y=background_y,
            r_squared=r_squared,
            concentration=concentration,
            title=f"Spectrum {self.current_spectrum_index + 1}/{self.total_spectra}: {filename}"
        )
        
        # Update info label
        info_text = f"R² = {r_squared:.4f} | Conc = {concentration:.2f} ppm | Center = {fit_params['center']:.3f} keV"
        self.spectrum_info_label.setText(info_text)
        
        # Update spinbox
        self.spectrum_spinbox.blockSignals(True)
        self.spectrum_spinbox.setValue(self.current_spectrum_index + 1)
        self.spectrum_spinbox.blockSignals(False)
        
        # Update navigation buttons
        self.prev_spectrum_btn.setEnabled(self.current_spectrum_index > 0)
        self.next_spectrum_btn.setEnabled(self.current_spectrum_index < self.total_spectra - 1)
    
    def show_previous_spectrum(self):
        """Show the previous spectrum"""
        if hasattr(self, 'current_spectrum_index') and self.current_spectrum_index > 0:
            self.current_spectrum_index -= 1
            self.show_current_spectrum()
    
    def show_next_spectrum(self):
        """Show the next spectrum"""
        if hasattr(self, 'current_spectrum_index') and self.current_spectrum_index < self.total_spectra - 1:
            self.current_spectrum_index += 1
            self.show_current_spectrum()
    
    def go_to_spectrum(self, spectrum_number):
        """Go to a specific spectrum number"""
        if hasattr(self, 'filtered_results') and self.filtered_results:
            index = spectrum_number - 1
            if 0 <= index < len(self.filtered_results):
                self.current_spectrum_index = index
                self.show_current_spectrum()
    
    def apply_r2_filter(self, min_r2):
        """Filter spectra by minimum R² value"""
        if not hasattr(self, 'batch_results') or not self.batch_results:
            return
        
        # Filter results by R²
        self.filtered_results = [r for r in self.batch_results if 'fit_params' in r and r['r_squared'] >= min_r2]
        
        if not self.filtered_results:
            self.spectrum_info_label.setText("No spectra meet R² filter criteria")
            self.prev_spectrum_btn.setEnabled(False)
            self.next_spectrum_btn.setEnabled(False)
            self.total_spectra_label.setText("0")
            self.spectrum_spinbox.setMaximum(1)
            return
        
        # Reset to first spectrum
        self.current_spectrum_index = 0
        self.total_spectra = len(self.filtered_results)
        
        # Update UI
        self.total_spectra_label.setText(str(self.total_spectra))
        self.spectrum_spinbox.setMaximum(self.total_spectra)
        self.spectrum_spinbox.setValue(1)
        
        # Enable controls
        self.prev_spectrum_btn.setEnabled(True)
        self.next_spectrum_btn.setEnabled(True)
        
        # Show first filtered spectrum
        self.show_current_spectrum()
    
    def show_sorting_dialog(self, file_paths, folder_path):
        """Show dialog for file sorting options"""
        dialog = FileSortingDialog(file_paths, folder_path, self)
        if dialog.exec() == QDialog.Accepted:
            self.sorted_file_paths = dialog.get_sorted_files()
            self.batch_file_paths = self.sorted_file_paths  # Set the batch file paths for processing
            self.batch_folder_label.setText(f"{len(self.sorted_file_paths)} files sorted and ready")
            self.fit_batch_btn.setEnabled(True)
    
    def natural_sort_key(self, filename):
        """Generate a key for natural sorting of filenames"""
        import re
        
        # Extract the base filename without path
        basename = os.path.basename(filename)
        
        # Split the filename into text and number parts
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        # Use regex to split on numbers
        alphanum_key = [convert(c) for c in re.split('([0-9]+)', basename)]
        return alphanum_key
    
    def smart_sort_files(self, file_paths):
        """Sort files using natural sorting (handles numbers correctly)"""
        return sorted(file_paths, key=self.natural_sort_key)
    
    def detect_sorting_pattern(self, file_paths):
        """Detect the naming pattern in the files"""
        if not file_paths:
            return "unknown"
        
        # Get just the filenames
        filenames = [os.path.basename(f) for f in file_paths]
        
        # Check for common patterns
        patterns = {
            "sample_number": r"sample_(\d+)",
            "sample_number_extended": r"sample_(\d+)_",
            "number_only": r"^(\d+)",
            "letter_number": r"([A-Za-z]+)(\d+)",
            "date_pattern": r"(\d{4})[-_](\d{2})[-_](\d{2})",
            "time_pattern": r"(\d{2})[-:](\d{2})[-:](\d{2})"
        }
        
        for pattern_name, pattern in patterns.items():
            matches = [re.search(pattern, f) for f in filenames]
            if all(matches):
                return pattern_name
        
        return "unknown"
    

    
    def show_statistics_plot(self):
        """Show the sample statistics plot"""
        if hasattr(self, 'sample_groups') and self.sample_groups:
            self.plot_canvas.plot_sample_statistics(self.sample_groups)
    
    def update_top_plot_zoom(self):
        """Update the plot zoom range and redraw if data is available"""
        self.plot_canvas.display_min = self.display_min_spin.value()
        self.plot_canvas.display_max = self.display_max_spin.value()
        
        # Redraw current spectrum if available
        if hasattr(self, 'current_data') and self.current_data is not None:
            x, y = self.current_data
            self.plot_canvas.plot_spectrum(x, y, title="XRF Spectrum")
        
        # Also update real-time plot if available
        if hasattr(self, 'latest_processed_data'):
            self.update_real_time_plot()

    def show_protocol_dialog(self):
        """Show the XRF SOP in a popup dialog with markdown formatting"""
        dialog = ProtocolDialog(self)
        dialog.exec()
    
    def export_protocol_text(self):
        """Export XRF SOP text to file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export XRF SOP", "xrf_sop.txt", "Text Files (*.txt)")
        if file_path:
            try:
                with open('xrf_sop_markdown.md', 'r') as f:
                    protocol_text = f.read()
                with open(file_path, 'w') as f:
                    f.write(protocol_text)
                QMessageBox.information(self, "Export Complete", f"XRF SOP exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Error exporting XRF SOP: {e}")
    
    def generate_all_sample_reports(self):
        """Generate reports for all samples"""
        if not hasattr(self, 'sample_groups') or not self.sample_groups:
            QMessageBox.warning(self, "Error", "No sample data available for report generation")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory for Reports")
        if not output_dir:
            return
        
        try:
            # Generate reports for each sample
            for i, sample_group in enumerate(self.sample_groups):
                self.generate_sample_report(sample_group, output_dir, f"Sample_{i+1}")
            
            QMessageBox.information(self, "Report Generation Complete", 
                                  f"Generated {len(self.sample_groups)} sample reports in {output_dir}")
            
        except Exception as e:
            QMessageBox.warning(self, "Report Generation Error", f"Error generating reports: {str(e)}")
    
    def generate_single_sample_report(self):
        """Generate a report for the currently selected sample"""
        if not hasattr(self, 'sample_groups') or not self.sample_groups:
            QMessageBox.warning(self, "Error", "No sample data available for report generation")
            return
        
        # Get current sample index
        if not hasattr(self, 'current_spectrum_index') or not hasattr(self, 'filtered_results'):
            QMessageBox.warning(self, "Error", "Please select a sample in the spectrum browser first")
            return
        
        # Find which sample the current spectrum belongs to
        sample_index = self.current_spectrum_index // self.spectra_per_sample_spin.value()
        if sample_index >= len(self.sample_groups):
            QMessageBox.warning(self, "Error", "Invalid sample index")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory for Report")
        if not output_dir:
            return
        
        try:
            sample_group = self.sample_groups[sample_index]
            self.generate_sample_report(sample_group, output_dir, f"Sample_{sample_index+1}")
            
            QMessageBox.information(self, "Report Generation Complete", 
                                  f"Generated report for {sample_group.sample_name} in {output_dir}")
            
        except Exception as e:
            QMessageBox.warning(self, "Report Generation Error", f"Error generating report: {str(e)}")
    
    def generate_sample_report(self, sample_group, output_dir, filename_prefix):
        """Generate a comprehensive report for a single sample"""
        report_format = self.report_format_combo.currentText()
        
        if report_format == "HTML":
            self.generate_html_report(sample_group, output_dir, filename_prefix)
        elif report_format == "PDF":
            self.generate_pdf_report(sample_group, output_dir, filename_prefix)
        # Word report option removed

    def generate_pdf_report(self, sample_group, output_dir, filename_prefix):
        """Generate PDF report for a sample (now matches HTML content)"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import pandas as pd

            # Create PDF file
            pdf_file = os.path.join(output_dir, f"{filename_prefix}_XRF_Report.pdf")
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            styles = getSampleStyleSheet()

            # Build PDF content
            story = []

            # Header with logos
            header_data = []
            # Left logo (Pb logo)
            if os.path.exists('Pb_logo.png'):
                pb_logo = Image('Pb_logo.png', width=1.5*inch, height=1*inch, kind='proportional')
                header_data.append(pb_logo)
            else:
                header_data.append(Paragraph("", styles['Normal']))
            # Center title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )
            header_data.append(Paragraph(f"XRF Analysis Report<br/>{sample_group.sample_name}", title_style))
            # Right logo (NHM logo)
            if os.path.exists('NHM_logo_black2.jpg'):
                nhm_logo = Image('NHM_logo_black2.jpg', width=1.5*inch, height=1*inch, kind='proportional')
                header_data.append(nhm_logo)
            else:
                header_data.append(Paragraph("", styles['Normal']))
            # Create header table
            header_table = Table([header_data], colWidths=[2*inch, 4*inch, 2*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 20))

            # Protocol Summary
            story.append(Paragraph("<b>Method:</b> XRF Analysis of Lead (Pb) in Pressed Pellets", styles['Normal']))
            story.append(Paragraph("<b>Peak:</b> Pb L-alpha at 10.5 keV", styles['Normal']))
            story.append(Paragraph("<b>Fitting:</b> Gaussian-A function with linear background", styles['Normal']))
            story.append(Paragraph("<b>Calibration:</b> NIST calibration curve (Concentration = 13.8913 × Intensity + 0)", styles['Normal']))
            story.append(Spacer(1, 12))

            # Sample Information
            story.append(Paragraph("<b>Sample Information</b>", styles['Heading2']))
            story.append(Paragraph(f"<b>Sample Name:</b> {sample_group.sample_name}", styles['Normal']))
            story.append(Paragraph(f"<b>Number of Spectra:</b> {sample_group.n_spectra}", styles['Normal']))
            story.append(Paragraph(f"<b>Analysis Date:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Statistical Summary Table
            story.append(Paragraph("<b>Statistical Summary</b>", styles['Heading2']))
            data = [
                ["Parameter", "Value", "Standard Deviation", "RSD (%)"],
                ["Mean Integrated Intensity", f"{sample_group.mean_integrated_intensity:.2f}", f"{sample_group.std_integrated_intensity:.2f}", f"{sample_group.rsd_integrated_intensity:.2f}"],
                ["Mean Concentration (ppm)", f"{sample_group.mean_concentration:.4f}", f"{sample_group.std_concentration:.4f}", f"{sample_group.rsd_concentration:.2f}"]
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))

            # Calibration Information
            story.append(Paragraph("<b>Calibration Information</b>", styles['Heading2']))
            story.append(Paragraph("<b>Calibration Equation:</b> Concentration = 13.8913 × Integrated Intensity + 0", styles['Normal']))
            story.append(Paragraph("<b>Calibration Source:</b> NIST Standard Reference Materials", styles['Normal']))
            story.append(Paragraph("<b>Dilution Factor:</b> 0.833 (2.0g sample + 0.4g binder)", styles['Normal']))
            story.append(Spacer(1, 12))

            # Quality Control
            story.append(Paragraph("<b>Quality Control</b>", styles['Heading2']))
            if sample_group.rsd_concentration <= 5.0:
                qc_status = "PASS"
                qc_color = colors.green
            else:
                qc_status = "FAIL"
                qc_color = colors.red
            qc_text = f"<b>Precision (RSD):</b> <font color='{qc_color.hexval()}'>{sample_group.rsd_concentration:.2f}% - {qc_status}</font>"
            story.append(Paragraph(qc_text, styles['Normal']))
            story.append(Paragraph("<b>Acceptance Criteria:</b> RSD ≤ 5.0%", styles['Normal']))

            # Build PDF
            doc.build(story)

        except ImportError:
            QMessageBox.warning(self, "PDF Generation Error", 
                              "PDF generation requires reportlab. Please install with: pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "PDF Generation Error", f"Error generating PDF: {str(e)}")

    def generate_html_report(self, sample_group, output_dir, filename_prefix):
        """Generate HTML report for a sample"""
        html_content = self.create_report_content(sample_group, "html")
        
        # Save HTML file
        html_file = os.path.join(output_dir, f"{filename_prefix}_XRF_Report.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Copy logo files to output directory for HTML display
        try:
            if os.path.exists('Pb_logo.png'):
                import shutil
                shutil.copy2('Pb_logo.png', output_dir)
            
            if os.path.exists('NHM_logo_black2.jpg'):
                import shutil
                shutil.copy2('NHM_logo_black2.jpg', output_dir)
        except Exception as e:
            print(f"Warning: Could not copy logo files: {e}")
    
    def create_report_content(self, sample_group, format_type):
        """Create the content for a report"""
        content = []
        
        # Header with logos
        content.append("<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;'>")
        
        # Left logo (Pb logo)
        if os.path.exists('Pb_logo.png'):
            content.append("<div style='flex: 1; text-align: left;'>")
            content.append("<img src='Pb_logo.png' alt='Pb Logo' style='max-height: 80px; max-width: 200px; object-fit: contain;'>")
            content.append("</div>")
        else:
            content.append("<div style='flex: 1;'></div>")
        
        # Center title
        content.append("<div style='flex: 2; text-align: center;'>")
        content.append(f"<h1 style='margin: 0;'>XRF Analysis Report - {sample_group.sample_name}</h1>")
        content.append("</div>")
        
        # Right logo (NHM logo)
        if os.path.exists('NHM_logo_black2.jpg'):
            content.append("<div style='flex: 1; text-align: right;'>")
            content.append("<img src='NHM_logo_black2.jpg' alt='NHM Logo' style='max-height: 80px; max-width: 200px; object-fit: contain;'>")
            content.append("</div>")
        else:
            content.append("<div style='flex: 1;'></div>")
        
        content.append("</div>")
        
        # Protocol Summary
        if self.include_protocol_check.isChecked():
            content.append("<h2>Protocol Summary</h2>")
            content.append("<p><strong>Method:</strong> XRF Analysis of Lead (Pb) in Pressed Pellets</p>")
            content.append("<p><strong>Peak:</strong> Pb L-alpha at 10.5 keV</p>")
            content.append("<p><strong>Fitting:</strong> Gaussian-A function with linear background</p>")
            content.append("<p><strong>Calibration:</strong> NIST calibration curve (Concentration = 13.8913 × Intensity + 0)</p>")
        
        # Sample Information
        content.append("<h2>Sample Information</h2>")
        content.append(f"<p><strong>Sample Name:</strong> {sample_group.sample_name}</p>")
        content.append(f"<p><strong>Number of Spectra:</strong> {sample_group.n_spectra}</p>")
        content.append(f"<p><strong>Analysis Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # Statistics Table
        if self.include_statistics_check.isChecked():
            content.append("<h2>Statistical Summary</h2>")
            content.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            content.append("<tr><th>Parameter</th><th>Value</th><th>Standard Deviation</th><th>RSD (%)</th></tr>")
            content.append(f"<tr><td>Mean Integrated Intensity</td><td>{sample_group.mean_integrated_intensity:.2f}</td><td>{sample_group.std_integrated_intensity:.2f}</td><td>{sample_group.rsd_integrated_intensity:.2f}</td></tr>")
            content.append(f"<tr><td>Mean Concentration (ppm)</td><td>{sample_group.mean_concentration:.4f}</td><td>{sample_group.std_concentration:.4f}</td><td>{sample_group.rsd_concentration:.2f}</td></tr>")
            content.append("</table>")
        
        # Calibration Information
        if self.include_calibration_check.isChecked():
            content.append("<h2>Calibration Information</h2>")
            content.append("<p><strong>Calibration Equation:</strong> Concentration = 13.8913 × Integrated Intensity + 0</p>")
            content.append("<p><strong>Calibration Source:</strong> NIST Standard Reference Materials</p>")
            content.append("<p><strong>Dilution Factor:</strong> 0.833 (2.0g sample + 0.4g binder)</p>")
        
        # Example Spectrum (if available)
        if self.include_spectra_check.isChecked() and hasattr(self, 'batch_results'):
            content.append("<h2>Example Spectrum</h2>")
            content.append("<p>Representative spectrum with Gaussian-A fit shown in the main application window.</p>")
            content.append("<p><strong>Peak Center:</strong> ~10.5 keV (Pb L-alpha)</p>")
            content.append("<p><strong>Integration Region:</strong> 9.8 - 11.2 keV</p>")
        
        # Quality Control
        content.append("<h2>Quality Control</h2>")
        if sample_group.rsd_concentration <= 5.0:
            qc_status = "PASS"
            qc_color = "green"
        else:
            qc_status = "FAIL"
            qc_color = "red"
        
        content.append(f"<p><strong>Precision (RSD):</strong> <span style='color: {qc_color};'>{sample_group.rsd_concentration:.2f}% - {qc_status}</span></p>")
        content.append("<p><strong>Acceptance Criteria:</strong> RSD ≤ 5.0%</p>")
        
        # HTML wrapper
        if format_type == "html":
            html_wrapper = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>XRF Report - {sample_group.sample_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f8f9fa; font-weight: bold; }}
                    .qc-pass {{ color: green; font-weight: bold; }}
                    .qc-fail {{ color: red; font-weight: bold; }}
                </style>
            </head>
            <body>
                {''.join(content)}
            </body>
            </html>
            """
            return html_wrapper
        
        return content
    
    def create_pdf_content(self, sample_group, styles):
        """Create content for PDF report"""
        story = []
        
        # Add content sections here (simplified for now)
        story.append(Paragraph(f"Sample: {sample_group.sample_name}", styles['Heading2']))
        story.append(Paragraph(f"Mean Concentration: {sample_group.mean_concentration:.4f} ppm", styles['Normal']))
        story.append(Paragraph(f"RSD: {sample_group.rsd_concentration:.2f}%", styles['Normal']))
        
        return story
    
    def create_word_content(self, doc, sample_group):
        """Create content for Word document"""
        # Add content sections here (simplified for now)
        doc.add_heading("Sample Information", level=2)
        doc.add_paragraph(f"Sample: {sample_group.sample_name}")
        doc.add_paragraph(f"Mean Concentration: {sample_group.mean_concentration:.4f} ppm")
        doc.add_paragraph(f"RSD: {sample_group.rsd_concentration:.2f}%")


class ProtocolDialog(QDialog):
    """Dialog for displaying the XRF SOP with markdown formatting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XRF Standard Operating Procedure")
        self.setGeometry(200, 200, 900, 700)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create text browser for markdown display
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setFont(QFont("Arial", 10))
        layout.addWidget(self.text_browser)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        # Load and format protocol
        self.load_protocol()
    
    def load_protocol(self):
        """Load and format the XRF SOP text"""
        try:
            with open('xrf_sop_markdown.md', 'r', encoding='utf-8') as f:
                protocol_text = f.read()
            
            # Convert markdown to HTML for display
            html_content = self.markdown_to_html(protocol_text)
            self.text_browser.setHtml(html_content)
            
        except Exception as e:
            self.text_browser.setPlainText(f"Could not load xrf_sop_markdown.md: {e}")
    
    def markdown_to_html(self, markdown_text):
        """Convert markdown text to HTML for display"""
        import re
        
        # Process code blocks first (to avoid interference with other formatting)
        code_blocks = []
        def replace_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        # Find and replace code blocks
        html = re.sub(r'```.*?\n.*?```', replace_code_block, markdown_text, flags=re.DOTALL)
        
        # Process headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Process tables (basic table support)
        def process_table(table_text):
            lines = table_text.strip().split('\n')
            if len(lines) < 3:
                return table_text
            
            html_table = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 15px 0;">'
            
            for i, line in enumerate(lines):
                if line.startswith('|') and line.endswith('|'):
                    # Remove leading/trailing pipes and split
                    cells = [cell.strip() for cell in line[1:-1].split('|')]
                    
                    if i == 0:
                        # Header row
                        html_table += '<tr style="background-color: #f8f9fa; font-weight: bold;">'
                        for cell in cells:
                            html_table += f'<td style="padding: 8px; border: 1px solid #ddd;">{cell}</td>'
                        html_table += '</tr>'
                    elif i == 1 and all(cell.replace('-', '').replace(':', '').replace('|', '').strip() == '' for cell in cells):
                        # Separator row - skip
                        continue
                    else:
                        # Data row
                        html_table += '<tr>'
                        for cell in cells:
                            html_table += f'<td style="padding: 8px; border: 1px solid #ddd;">{cell}</td>'
                        html_table += '</tr>'
            
            html_table += '</table>'
            return html_table
        
        # Find and replace tables
        table_pattern = r'(\|.*\|\n\|[\s\-:|]*\|\n(\|.*\|\n)*)'
        tables = re.findall(table_pattern, html)
        for table in tables:
            html = html.replace(table[0], process_table(table[0]))
        
        # Process lists
        html = re.sub(r'^\s*[-*]\s+(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\s*\d+\.\s+(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Process bold and italic (handle nested formatting)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
        
        # Process inline code
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Process horizontal rules
        html = re.sub(r'^---$', r'<hr style="border: none; border-top: 2px solid #3498db; margin: 20px 0;">', html, flags=re.MULTILINE)
        
        # Restore code blocks
        for i, code_block in enumerate(code_blocks):
            # Extract language and content
            lines = code_block.strip().split('\n')
            if lines[0].startswith('```'):
                lang = lines[0][3:].strip()
                content = '\n'.join(lines[1:-1])
                html = html.replace(f"__CODE_BLOCK_{i}__", 
                                  f'<pre><code class="{lang}">{content}</code></pre>')
        
        # Process paragraphs
        html = re.sub(r'\n\n+', '</p>\n<p>', html)
        html = re.sub(r'\n', '<br>', html)
        
        # Wrap in HTML structure with improved styling
        html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{ 
                    color: #2c3e50; 
                    border-bottom: 3px solid #3498db; 
                    padding-bottom: 10px; 
                    margin-top: 30px;
                    font-size: 24px;
                }}
                h2 {{ 
                    color: #34495e; 
                    margin-top: 25px; 
                    margin-bottom: 15px;
                    font-size: 20px;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }}
                h3 {{ 
                    color: #7f8c8d; 
                    margin-top: 20px;
                    margin-bottom: 10px;
                    font-size: 16px;
                }}
                code {{ 
                    background-color: #f8f9fa; 
                    padding: 2px 6px; 
                    border-radius: 4px; 
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 0.9em;
                    color: #e74c3c;
                }}
                pre {{ 
                    background-color: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 8px; 
                    border-left: 4px solid #3498db;
                    margin: 15px 0;
                    overflow-x: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                    color: #333;
                }}
                li {{ 
                    margin: 8px 0; 
                    padding-left: 10px;
                }}
                strong {{ 
                    color: #e74c3c; 
                    font-weight: bold;
                }}
                em {{
                    color: #27ae60;
                    font-style: italic;
                }}
                p {{
                    margin: 10px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                hr {{
                    border: none;
                    border-top: 2px solid #3498db;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <p>{html}</p>
        </body>
        </html>
        """
        
        return html

def parse_emsa_file_pandas(filename):
    """
    Parse EMSA/MAS spectral data file and return metadata dict and spectral DataFrame.
    
    Parameters:
    -----------
    filename : str or Path
        Path to the EMSA file
        
    Returns:
    --------
    metadata : dict
        Dictionary containing all header metadata
    spectrum_df : pandas.DataFrame
        DataFrame with columns ['energy_kev', 'counts']
    """
    metadata = {}
    data_lines = []
    
    with open(filename, 'r') as f:
        in_data = False
        for line in f:
            line = line.strip()
            
            # Check for data section start
            if line.startswith('#SPECTRUM'):
                in_data = True
                continue
                
            # Check for data section end
            if line.startswith('#ENDOFDATA'):
                break
                
            # Parse metadata (lines starting with #)
            if not in_data and line.startswith('#'):
                if ':' in line:
                    # Handle standard format: #KEY : VALUE
                    key, value = line[1:].split(':', 1)
                    metadata[key.strip()] = value.strip()
                else:
                    # Handle special format: ##KEY   : VALUE
                    parts = line[1:].split(None, 1)
                    if len(parts) == 2:
                        metadata[parts[0].strip()] = parts[1].strip()
                continue
                
            # Parse spectral data
            if in_data and line and not line.startswith('#'):
                try:
                    x, y = map(float, line.split(','))
                    data_lines.append([x, y])
                except ValueError:
                    continue
    
    # Create DataFrame
    spectrum_df = pd.DataFrame(data_lines, columns=['energy_kev', 'counts'])
    
    return metadata, spectrum_df

def load_multiple_emsa_files(file_pattern="*.txt"):
    """
    Load multiple EMSA files and return a dictionary of metadata and DataFrames.
    
    Parameters:
    -----------
    file_pattern : str
        Glob pattern to match EMSA files
        
    Returns:
    --------
    data_dict : dict
        Dictionary with filename as key, containing 'metadata' and 'spectrum' keys
    """
    data_dict = {}
    
    for file_path in Path('.').glob(file_pattern):
        if file_path.is_file():
            try:
                metadata, spectrum_df = parse_emsa_file_pandas(file_path)
                data_dict[file_path.name] = {
                    'metadata': metadata,
                    'spectrum': spectrum_df
                }
                print(f"Loaded: {file_path.name}")
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
    
    return data_dict

def plot_spectrum(spectrum_df, metadata=None, title=None, ax=None):
    """
    Plot a single spectrum with optional metadata annotation.
    
    Parameters:
    -----------
    spectrum_df : pandas.DataFrame
        DataFrame with 'energy_kev' and 'counts' columns
    metadata : dict, optional
        Metadata dictionary for annotation
    title : str, optional
        Plot title
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    """
    # Apply compact theme if available
    try:
        apply_theme('compact')
    except:
        pass
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(spectrum_df['energy_kev'], spectrum_df['counts'], linewidth=1.5)
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('Counts')
    
    if title:
        ax.set_title(title)
    elif metadata and 'TITLE' in metadata:
        ax.set_title(metadata['TITLE'])
    
    # Add metadata annotation if provided
    if metadata:
        info_text = f"Live time: {metadata.get('LIVETIME', 'N/A')} s\n"
        info_text += f"Beam kV: {metadata.get('BEAMKV', 'N/A')} kV\n"
        info_text += f"Date: {metadata.get('DATE', 'N/A')}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.grid(True, alpha=0.3)
    return ax

def plot_multiple_spectra(data_dict, elements_to_highlight=None):
    """
    Plot multiple spectra on the same axes.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary of loaded spectra data
    elements_to_highlight : list, optional
        List of energy values to highlight (e.g., element peaks)
    """
    # Apply compact theme if available
    try:
        apply_theme('compact')
    except:
        pass
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(data_dict)))
    
    for (filename, data), color in zip(data_dict.items(), colors):
        spectrum_df = data['spectrum']
        metadata = data['metadata']
        
        label = metadata.get('TITLE', filename)
        ax.plot(spectrum_df['energy_kev'], spectrum_df['counts'], 
                label=label, linewidth=1.5, color=color)
    
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('Counts')
    ax.set_title('XRF Spectra Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Highlight specific elements if provided
    if elements_to_highlight:
        for element_energy in elements_to_highlight:
            ax.axvline(x=element_energy, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return fig, ax

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = XRFPeakFittingGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()