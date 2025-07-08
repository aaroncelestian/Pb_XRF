import sys
import os
import re
import json
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QFileDialog, QLabel, QLineEdit,
                               QTextEdit, QProgressBar, QGridLayout, QGroupBox,
                               QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                               QTableWidget, QTableWidgetItem, QTabWidget,
                               QMessageBox, QSplitter, QScrollArea, QDialog,
                               QDialogButtonBox, QTextBrowser, QProgressDialog,
                               QListWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    except ImportError:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy import integrate, stats
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
        # Custom calibration name
        self.calibration_name = "NIST Calibration"
        
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
        
        # Initialize subplots immediately
        self.setup_subplots()
        
        # Store current data for zoom updates
        self.current_spectrum_data = None
        
        # Connect to zoom/pan events for auto Y-scaling
        self.setup_zoom_events()
        
    def setup_zoom_events(self):
        """Setup event handlers for zoom/pan to trigger Y-axis auto-scaling"""
        try:
            # Connect to xlim change events (fired when user zooms or pans)
            if hasattr(self, 'ax1'):
                self.ax1.callbacks.connect('xlim_changed', self.on_xlim_changed)
        except Exception as e:
            print(f"Warning: Could not setup zoom events: {e}")
    
    def on_xlim_changed(self, ax):
        """Called when X-axis limits change (zoom/pan)"""
        try:
            if self.current_spectrum_data is not None:
                x, y, fit_x, fit_y, background_x, background_y = self.current_spectrum_data
                x_min, x_max = ax.get_xlim()
                self.update_y_limits_for_zoom(x, y, fit_x, fit_y, background_x, background_y, x_min, x_max)
                self.draw_idle()  # Use draw_idle for better performance
        except Exception as e:
            print(f"Error in xlim_changed handler: {e}")
    
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
        try:
            # Ensure subplots are set up
            if not hasattr(self, 'ax1'):
                self.setup_subplots()
                self.setup_zoom_events()  # Reconnect events after subplot setup

            # Store current spectrum data for zoom event handling
            self.current_spectrum_data = (x, y, fit_x, fit_y, background_x, background_y)

            # 1. Save current zoom window (if any), else use display_min/max or default
            try:
                x_min, x_max = self.ax1.get_xlim()
                # If the current zoom is the default (0, 1), use display_min/max or default
                if x_min == 0.0 and x_max == 1.0:
                    raise Exception()
            except:
                if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
                    x_min, x_max = self.display_min, self.display_max
                else:
                    x_min, x_max = 9.5, 11.5

            # 2. Clear and plot with ORIGINAL intensity values (no normalization)
            self.ax1.clear()
            
            # Reconnect zoom events after clearing (clearing removes callbacks)
            self.ax1.callbacks.connect('xlim_changed', self.on_xlim_changed)
            
            self.ax1.plot(x, y, 'b-', linewidth=1, label='Raw Data', alpha=0.7)
            if background_x is not None and background_y is not None:
                self.ax1.plot(background_x, background_y, 'g--', linewidth=1.5, label='Background', alpha=0.8)
            if fit_x is not None and fit_y is not None:
                self.ax1.plot(fit_x, fit_y, 'r-', linewidth=2, label='Gaussian-A Fit')

            self.ax1.set_xlabel('Energy (keV)')
            self.ax1.set_ylabel('Intensity (counts)')
            if r_squared is not None:
                title_with_r2 = f"{title} (R² = {r_squared:.4f})"
            else:
                title_with_r2 = title
            self.ax1.set_title(title_with_r2)
            self.ax1.grid(True, alpha=0.3)
            if concentration is not None:
                legend_text = f'Pb: {concentration:.2f} ppm'
                self.ax1.text(0.02, 0.98, legend_text, transform=self.ax1.transAxes, 
                             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                             fontsize=10, fontweight='bold')
            self.ax1.legend()
            self.ax1.axvspan(10.0, 11.0, alpha=0.2, color='yellow', label='Pb Peak Region')

            # 3. Restore X zoom window
            self.ax1.set_xlim(x_min, x_max)
            
            # 4. Auto-scale Y-axis based only on data within the current X zoom window
            self.update_y_limits_for_zoom(x, y, fit_x, fit_y, background_x, background_y, x_min, x_max)
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            print(f"Error in plot_spectrum: {e}")
            try:
                self.setup_subplots()
                self.setup_zoom_events()
                self.ax1.clear()
                self.ax1.plot(x, y, 'b-', linewidth=1, label='Raw Data', alpha=0.7)
                self.ax1.set_xlabel('Energy (keV)')
                self.ax1.set_ylabel('Intensity (counts)')
                self.ax1.set_title(title)
                self.ax1.grid(True, alpha=0.3)
                self.ax1.legend()
                self.fig.tight_layout()
                self.draw()
            except Exception as e2:
                print(f"Failed to recover from plotting error: {e2}")
    
    def update_y_limits_for_zoom(self, x, y, fit_x=None, fit_y=None, background_x=None, background_y=None, x_min=None, x_max=None):
        """Update Y-axis limits based on data within the current X zoom window"""
        try:
            # Get current X limits if not provided
            if x_min is None or x_max is None:
                x_min, x_max = self.ax1.get_xlim()
            
            # Collect all Y values within the X zoom window
            all_y_values = []
            
            # Raw data within zoom window
            mask = (x >= x_min) & (x <= x_max)
            if mask.any():
                all_y_values.extend(y[mask])
            
            # Fit data within zoom window
            if fit_x is not None and fit_y is not None:
                fit_mask = (fit_x >= x_min) & (fit_x <= x_max)
                if fit_mask.any():
                    all_y_values.extend(fit_y[fit_mask])
            
            # Background data within zoom window
            if background_x is not None and background_y is not None:
                bg_mask = (background_x >= x_min) & (background_x <= x_max)
                if bg_mask.any():
                    all_y_values.extend(background_y[bg_mask])
            
            # Calculate Y limits with some padding
            if all_y_values:
                y_min = min(all_y_values)
                y_max = max(all_y_values)
                
                # Add 5% padding on both sides
                y_range = y_max - y_min
                if y_range > 0:
                    padding = 0.05 * y_range
                    new_y_min = y_min - padding
                    new_y_max = y_max + padding
                    self.ax1.set_ylim(new_y_min, new_y_max)
                else:
                    # If all values are the same, add some default padding
                    self.ax1.set_ylim(y_min - 1, y_max + 1)
            else:
                # Fallback: use full data range
                self.ax1.set_ylim(y.min(), y.max())
                
        except Exception as e:
            print(f"Error updating Y limits: {e}")
            # Fallback: use automatic scaling
            try:
                self.ax1.relim()
                self.ax1.autoscale_view()
            except:
                pass
    
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
        
        # Plot calibration line using CURRENT calibration parameters
        if mean_intensities:
            x_cal = np.linspace(min(mean_intensities), max(mean_intensities), 100)
            
            # Try to get current calibration parameters from parent GUI
            try:
                # Access the GUI through the parent chain
                gui_parent = self.parent()
                while gui_parent and not hasattr(gui_parent, 'fitter'):
                    gui_parent = gui_parent.parent()
                
                if gui_parent and hasattr(gui_parent, 'fitter'):
                    slope = gui_parent.fitter.calibration_slope
                    intercept = gui_parent.fitter.calibration_intercept
                    cal_name = getattr(gui_parent.fitter, 'calibration_name', None)
                    
                    # Determine calibration type for label
                    if cal_name:
                        cal_label = cal_name
                    elif abs(slope - 13.8913) < 0.0001 and abs(intercept - 0.0) < 0.0001:
                        cal_label = 'NIST Calibration'
                    else:
                        cal_label = 'Custom Calibration'
                else:
                    # Fallback to default NIST values
                    slope = 13.8913
                    intercept = 0.0
                    cal_label = 'NIST Calibration'
            except:
                # Fallback to default NIST values
                slope = 13.8913
                intercept = 0.0
                cal_label = 'NIST Calibration'
            
            y_cal = slope * x_cal + intercept
            self.ax3.plot(x_cal, y_cal, 'r--', linewidth=2, label=cal_label)
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
        """Read XRF data from various file formats using smart detection"""
        try:
            # Use the smart parser that automatically detects file format
            x, y, format_type = parse_xrf_file_smart(file_path)
            
            if x is not None and y is not None:
                print(f"Successfully parsed {os.path.basename(file_path)} as {format_type} format")
                return x, y
            else:
                print(f"Failed to parse {file_path} with smart parser")
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
        
        # Custom calibration button
        self.custom_calibration_btn = QPushButton("🧪 Create Custom Calibration")
        self.custom_calibration_btn.clicked.connect(self.show_custom_calibration_dialog)
        self.custom_calibration_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        calibration_layout.addWidget(self.custom_calibration_btn, 4, 0, 1, 2)
        
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
            try:
                from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
                self.plot_toolbar = NavigationToolbar2QT(self.plot_canvas, self)
            except ImportError:
                try:
                    from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
                    self.plot_toolbar = NavigationToolbar2QT(self.plot_canvas, self)
                except ImportError:
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
    
    def show_custom_calibration_dialog(self):
        """Show the custom calibration dialog"""
        try:
            dialog = CustomCalibrationDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening custom calibration dialog: {str(e)}")
            print(f"Custom calibration dialog error: {e}")  # For debugging
    
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
        """Read XRF data from file using smart format detection"""
        try:
            # Use the smart parser that automatically detects file format
            x, y, format_type = parse_xrf_file_smart(file_path)
            
            if x is not None and y is not None:
                print(f"Successfully parsed {os.path.basename(file_path)} as {format_type} format")
                return x, y
            else:
                print(f"Failed to parse {file_path} with smart parser")
                return None
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def fit_single_file(self):
        """Fit a single XRF file"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            QMessageBox.warning(self, "Error", "No file loaded. Please select a file first.")
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
            
            # Store fit results for zoom updates
            self.current_fit_results = {
                'fit_params': fit_params,
                'fit_curve': fit_curve,
                'r_squared': r_squared,
                'x_fit': x_fit,
                'integrated_intensity': integrated_intensity,
                'concentration': concentration
            }
            
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
            
            # Store background for zoom updates
            self.current_background = {'x': background_x, 'y': background_y}
            
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
        
        # Store current data for zoom updates
        self.current_data = (x, y)
        
        # Store fit results for zoom updates
        self.current_fit_results = {
            'fit_params': fit_params,
            'fit_curve': fit_y,
            'r_squared': r_squared,
            'x_fit': fit_x,
            'integrated_intensity': result.get('integrated_intensity', 0),
            'concentration': concentration
        }
        
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
        
        # Store background for zoom updates
        self.current_background = {'x': background_x, 'y': background_y}
        
        # Calculate sample and spectrum numbers for title
        # Get spectra per sample from the main GUI
        spectra_per_sample = getattr(self, 'spectra_per_sample_spin', None)
        if spectra_per_sample:
            spectra_per_sample_value = spectra_per_sample.value()
        else:
            spectra_per_sample_value = 6  # Default value
        
        # Calculate which sample this spectrum belongs to
        sample_number = (self.current_spectrum_index // spectra_per_sample_value) + 1
        spectrum_in_sample = (self.current_spectrum_index % spectra_per_sample_value) + 1
        
        # Create enhanced title with sample and spectrum information
        title = f"Sample {sample_number}, Spectrum {spectrum_in_sample}/{spectra_per_sample_value} (Overall: {self.current_spectrum_index + 1}/{self.total_spectra}): {filename}"
        
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
            title=title
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
            
            # Check if we have fit results to redraw
            if hasattr(self, 'current_fit_results') and self.current_fit_results:
                fit_results = self.current_fit_results
                background = getattr(self, 'current_background', {'x': None, 'y': None})
                
                # Generate enhanced title if this is part of batch processing
                if hasattr(self, 'current_spectrum_index') and hasattr(self, 'total_spectra'):
                    # Get spectra per sample value
                    spectra_per_sample_value = getattr(self.spectra_per_sample_spin, 'value', lambda: 6)()
                    
                    # Calculate which sample this spectrum belongs to
                    sample_number = (self.current_spectrum_index // spectra_per_sample_value) + 1
                    spectrum_in_sample = (self.current_spectrum_index % spectra_per_sample_value) + 1
                    
                    title = f"Sample {sample_number}, Spectrum {spectrum_in_sample}/{spectra_per_sample_value} (Overall: {self.current_spectrum_index + 1}/{self.total_spectra}): {os.path.basename(self.current_file_path)}"
                else:
                    title = f"XRF Spectrum with Gaussian-A Fit - {os.path.basename(self.current_file_path)}"
                
                self.plot_canvas.plot_spectrum(
                    x, y,
                    fit_x=fit_results['x_fit'],
                    fit_y=fit_results['fit_curve'],
                    background_x=background['x'],
                    background_y=background['y'],
                    r_squared=fit_results['r_squared'],
                    concentration=fit_results['concentration'],
                    title=title
                )
            else:
                # Just raw data
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


class CustomCalibrationDialog(QDialog):
    """Dialog for creating custom calibrations using user's NIST standards"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Calibration Manager")
        self.setGeometry(200, 200, 1000, 700)
        
        # Initialize data storage
        self.standards_data = {
            'SRM_2586': {'files': [], 'intensities': [], 'mean': 0, 'std': 0, 'rsd': 0, 'concentration': 432},
            'SRM_2587': {'files': [], 'intensities': [], 'mean': 0, 'std': 0, 'rsd': 0, 'concentration': 3242}
        }
        self.calibration_results = None
        self.peak_fitter = XRFPeakFitter()
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Calibration name input at the top
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Calibration Name:"))
        self.calibration_name_edit = QLineEdit("My Custom Calibration")
        self.calibration_name_edit.setPlaceholderText("Enter a descriptive name for your calibration...")
        name_layout.addWidget(self.calibration_name_edit)
        layout.addLayout(name_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.setup_standards_tab()
        self.setup_calibration_tab()
        self.setup_validation_tab()
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Calibration")
        self.save_btn.clicked.connect(self.save_calibration)
        self.save_btn.setEnabled(False)
        
        self.load_btn = QPushButton("📂 Load Calibration")
        self.load_btn.clicked.connect(self.load_calibration)
        
        self.apply_btn = QPushButton("✅ Apply to Analysis")
        self.apply_btn.clicked.connect(self.apply_calibration)
        self.apply_btn.setEnabled(False)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def setup_standards_tab(self):
        """Setup the standards configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Instructions
        instructions = QLabel(
            "Load XRF spectrum files for each NIST standard. "
            "Multiple files per standard will be averaged for better precision."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        layout.addWidget(instructions)
        
        # Standards setup
        for std_name, std_data in self.standards_data.items():
            group_box = self.create_standard_group(std_name, std_data)
            layout.addWidget(group_box)
        
        # Calculate button
        calc_layout = QHBoxLayout()
        calc_layout.addStretch()
        self.calc_btn = QPushButton("🧮 Calculate Calibration")
        self.calc_btn.clicked.connect(self.calculate_calibration)
        self.calc_btn.setEnabled(False)
        calc_layout.addWidget(self.calc_btn)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)
        
        layout.addStretch()
        self.tabs.addTab(tab, "📊 Standards Setup")
    
    def create_standard_group(self, std_name, std_data):
        """Create a group box for a single standard"""
        conc = std_data['concentration']
        group_box = QGroupBox(f"{std_name} ({conc} ppm Pb)")
        layout = QVBoxLayout(group_box)
        
        # File management
        file_layout = QHBoxLayout()
        
        add_btn = QPushButton("📁 Add Files")
        add_btn.clicked.connect(lambda: self.add_files(std_name))
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(lambda: self.clear_files(std_name))
        
        file_layout.addWidget(add_btn)
        file_layout.addWidget(clear_btn)
        file_layout.addStretch()
        
        layout.addLayout(file_layout)
        
        # File list
        file_list = QListWidget()
        file_list.setMaximumHeight(80)
        layout.addWidget(file_list)
        std_data['file_list_widget'] = file_list
        
        # Results display
        results_layout = QHBoxLayout()
        
        mean_label = QLabel("Mean: -- cps")
        std_label = QLabel("Std Dev: -- cps")
        rsd_label = QLabel("RSD: -- %")
        
        results_layout.addWidget(mean_label)
        results_layout.addWidget(std_label)
        results_layout.addWidget(rsd_label)
        results_layout.addStretch()
        
        layout.addLayout(results_layout)
        
        # Store references
        std_data['mean_label'] = mean_label
        std_data['std_label'] = std_label
        std_data['rsd_label'] = rsd_label
        
        return group_box
    
    def setup_calibration_tab(self):
        """Setup the calibration results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Results display
        self.calibration_text = QTextEdit()
        self.calibration_text.setReadOnly(True)
        self.calibration_text.setMaximumHeight(150)
        layout.addWidget(self.calibration_text)
        
        # Plot area
        self.calibration_plot = PlotCanvas()
        layout.addWidget(self.calibration_plot)
        
        self.tabs.addTab(tab, "📈 Calibration Results")
    
    def setup_validation_tab(self):
        """Setup the validation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Validation results
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        layout.addWidget(self.validation_text)
        
        self.tabs.addTab(tab, "✅ Validation")
    
    def add_files(self, std_name):
        """Add files for a standard"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            f"Select {std_name} Files",
            "",
            "XRF Files (*.txt *.csv *.xlsx *.dat *.emsa *.spc);;All Files (*)"
        )
        
        if file_paths:
            self.standards_data[std_name]['files'].extend(file_paths)
            self.update_file_list(std_name)
            self.analyze_standard(std_name)
    
    def clear_files(self, std_name):
        """Clear files for a standard"""
        self.standards_data[std_name]['files'].clear()
        self.standards_data[std_name]['intensities'].clear()
        self.update_file_list(std_name)
        self.update_standard_results(std_name)
        self.check_calculation_ready()
    
    def update_file_list(self, std_name):
        """Update the file list display"""
        widget = self.standards_data[std_name]['file_list_widget']
        widget.clear()
        
        for file_path in self.standards_data[std_name]['files']:
            item_text = os.path.basename(file_path)
            widget.addItem(item_text)
    
    def analyze_standard(self, std_name):
        """Analyze all files for a standard"""
        files = self.standards_data[std_name]['files']
        intensities = []
        
        # Progress dialog
        progress = QProgressDialog(f"Analyzing {std_name} files...", "Cancel", 0, len(files), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            for i, file_path in enumerate(files):
                if progress.wasCanceled():
                    break
                
                progress.setValue(i)
                QApplication.processEvents()
                
                # Read and analyze file
                try:
                    x, y = self.read_xrf_file(file_path)
                    if x is not None and y is not None:
                        # Fit peak and get intensity
                        fit_params, fit_curve, r_squared, x_fit, integrated_intensity, concentration = self.peak_fitter.fit_peak(x, y)
                        if integrated_intensity is not None:
                            intensities.append(integrated_intensity)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
                    continue
            
            progress.setValue(len(files))
            
            # Store results
            self.standards_data[std_name]['intensities'] = intensities
            self.calculate_standard_stats(std_name)
            self.update_standard_results(std_name)
            self.check_calculation_ready()
            
        except Exception as e:
            QMessageBox.warning(self, "Analysis Error", f"Error analyzing {std_name}: {e}")
        
        progress.close()
    
    def read_xrf_file(self, file_path):
        """Read XRF file data using smart format detection"""
        try:
            # Use the smart parser that automatically detects file format
            x, y, format_type = parse_xrf_file_smart(file_path)
            
            if x is not None and y is not None:
                print(f"Successfully parsed {os.path.basename(file_path)} as {format_type} format")
                return x, y
            else:
                print(f"Failed to parse {file_path} with smart parser")
                return None, None
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None, None
    
    def calculate_standard_stats(self, std_name):
        """Calculate statistics for a standard"""
        intensities = self.standards_data[std_name]['intensities']
        
        if intensities:
            intensities = np.array(intensities)
            mean_int = np.mean(intensities)
            std_int = np.std(intensities, ddof=1) if len(intensities) > 1 else 0
            rsd_int = (std_int / mean_int * 100) if mean_int > 0 else 0
            
            self.standards_data[std_name]['mean'] = mean_int
            self.standards_data[std_name]['std'] = std_int
            self.standards_data[std_name]['rsd'] = rsd_int
    
    def update_standard_results(self, std_name):
        """Update the results display for a standard"""
        std_data = self.standards_data[std_name]
        
        if std_data['intensities']:
            std_data['mean_label'].setText(f"Mean: {std_data['mean']:.0f} cps")
            std_data['std_label'].setText(f"Std Dev: {std_data['std']:.0f} cps")
            std_data['rsd_label'].setText(f"RSD: {std_data['rsd']:.1f}%")
        else:
            std_data['mean_label'].setText("Mean: -- cps")
            std_data['std_label'].setText("Std Dev: -- cps")
            std_data['rsd_label'].setText("RSD: -- %")
    
    def check_calculation_ready(self):
        """Check if calibration calculation can be performed"""
        ready = all(
            len(std_data['intensities']) > 0 
            for std_data in self.standards_data.values()
        )
        self.calc_btn.setEnabled(ready)
    
    def calculate_calibration(self):
        """Calculate the custom calibration"""
        try:
            # Prepare data for linear regression
            concentrations = []
            intensities = []
            
            for std_data in self.standards_data.values():
                concentrations.append(std_data['concentration'])
                intensities.append(std_data['mean'])
            
            concentrations = np.array(concentrations)
            intensities = np.array(intensities)
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(intensities, concentrations)
            
            # Store results
            self.calibration_results = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'std_error': std_err,
                'concentrations': concentrations,
                'intensities': intensities,
                'name': self.calibration_name_edit.text().strip() or "Custom Calibration"
            }
            
            # Update displays
            self.update_calibration_display()
            self.create_calibration_plot()
            self.perform_validation()
            
            # Enable save and apply buttons
            self.save_btn.setEnabled(True)
            self.apply_btn.setEnabled(True)
            
            # Switch to results tab
            self.tabs.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error calculating calibration: {e}")
    
    def update_calibration_display(self):
        """Update the calibration results display"""
        if not self.calibration_results:
            return
        
        results = self.calibration_results
        
        # Format calibration equation
        equation = f"Concentration = {results['slope']:.6f} × Intensity + {results['intercept']:.2f}"
        
        text = f"""
Custom Calibration Results
========================

Calibration Equation:
{equation}

Statistical Parameters:
• R-squared: {results['r_squared']:.6f}
• Standard Error: {results['std_error']:.6f}
• P-value: {results['p_value']:.2e}

Standards Data:
• SRM 2586 (432 ppm): {self.standards_data['SRM_2586']['mean']:.0f} ± {self.standards_data['SRM_2586']['std']:.0f} cps
• SRM 2587 (3242 ppm): {self.standards_data['SRM_2587']['mean']:.0f} ± {self.standards_data['SRM_2587']['std']:.0f} cps
        """
        
        self.calibration_text.setPlainText(text.strip())
    
    def create_calibration_plot(self):
        """Create the calibration plot"""
        if not self.calibration_results:
            return
        
        results = self.calibration_results
        
        # Clear previous plot
        self.calibration_plot.figure.clear()
        ax = self.calibration_plot.figure.add_subplot(111)
        
        # Plot data points
        ax.scatter(results['intensities'], results['concentrations'], 
                  color='red', s=100, alpha=0.7, label='Custom Standards', zorder=5)
        
        # Plot calibration line
        x_range = np.linspace(0, max(results['intensities']) * 1.1, 100)
        y_pred = results['slope'] * x_range + results['intercept']
        cal_name = results.get('name', 'Custom Calibration')
        ax.plot(x_range, y_pred, 'r-', linewidth=2, label=cal_name, alpha=0.8)
        
        # Plot NIST calibration for comparison
        nist_slope = 3.297e-4
        nist_intercept = 0
        y_nist = nist_slope * x_range + nist_intercept
        ax.plot(x_range, y_nist, 'b--', linewidth=2, label='NIST Calibration', alpha=0.8)
        
        # Add error bars
        for i, std_name in enumerate(['SRM_2586', 'SRM_2587']):
            std_data = self.standards_data[std_name]
            if std_data['std'] > 0:
                ax.errorbar(std_data['mean'], std_data['concentration'], 
                           xerr=std_data['std'], fmt='none', color='red', alpha=0.5)
        
        ax.set_xlabel('Integrated Intensity (cps)')
        ax.set_ylabel('Pb Concentration (ppm)')
        ax.set_title(f"{cal_name} (R² = {results['r_squared']:.6f})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Set reasonable axis limits
        ax.set_xlim(0, max(results['intensities']) * 1.1)
        ax.set_ylim(0, max(results['concentrations']) * 1.1)
        
        self.calibration_plot.draw()
    
    def perform_validation(self):
        """Perform validation analysis"""
        if not self.calibration_results:
            return
        
        results = self.calibration_results
        
        # Calculate machine-dependent quality thresholds based on standards performance
        std_rsds = []
        for std_name, std_data in self.standards_data.items():
            if std_data['rsd'] > 0:
                std_rsds.append(std_data['rsd'])
        
        if std_rsds:
            # Use the average RSD of standards as baseline, with some tolerance
            avg_rsd = np.mean(std_rsds)
            max_rsd = np.max(std_rsds)
            
            # Set quality thresholds based on actual instrument performance
            excellent_threshold = avg_rsd * 0.8  # 20% better than average
            good_threshold = avg_rsd * 1.2       # 20% worse than average
            acceptable_threshold = max_rsd * 1.5  # 50% worse than worst standard
        else:
            # Fallback to reasonable defaults if no standards data
            excellent_threshold = 3.0
            good_threshold = 5.0
            acceptable_threshold = 8.0
        
        # Quality assessment for calibration fit
        r_squared = results['r_squared']
        if r_squared >= 0.995:
            quality = "Excellent"
            quality_color = "green"
        elif r_squared >= 0.99:
            quality = "Good"
            quality_color = "orange"
        elif r_squared >= 0.98:
            quality = "Acceptable"
            quality_color = "orange"
        else:
            quality = "Poor"
            quality_color = "red"
        
        # Calculate recovery for each standard
        recovery_text = ""
        all_recoveries_good = True
        
        for std_name, std_data in self.standards_data.items():
            predicted_conc = results['slope'] * std_data['mean'] + results['intercept']
            recovery = (predicted_conc / std_data['concentration']) * 100
            recovery_text += f"• {std_name}: {recovery:.1f}% recovery\n"
            
            if recovery < 95 or recovery > 105:
                all_recoveries_good = False
        
        # Precision assessment using dynamic thresholds
        rsd_2586 = self.standards_data['SRM_2586']['rsd']
        rsd_2587 = self.standards_data['SRM_2587']['rsd']
        max_rsd = max(rsd_2586, rsd_2587)
        precision_good = max_rsd <= acceptable_threshold
        
        # Overall recommendation
        if r_squared >= 0.995 and all_recoveries_good and precision_good:
            recommendation = "✅ RECOMMENDED: This calibration meets all quality criteria."
            rec_color = "green"
        elif r_squared >= 0.99 and (all_recoveries_good or precision_good):
            recommendation = "⚠️ ACCEPTABLE: This calibration meets most quality criteria."
            rec_color = "orange"
        else:
            recommendation = "❌ NOT RECOMMENDED: This calibration has quality issues."
            rec_color = "red"
        
        validation_text = f"""
Calibration Validation Report
============================

R-squared Quality Assessment:
• Value: {r_squared:.6f}
• Rating: {quality}
• Criterion: ≥0.995 (Excellent), ≥0.99 (Good), ≥0.98 (Acceptable)

Standard Recovery Analysis:
{recovery_text}• Target Range: 95-105%

Precision Assessment (Machine-Dependent):
• SRM 2586 RSD: {rsd_2586:.1f}%
• SRM 2587 RSD: {rsd_2587:.1f}%
• Average Standards RSD: {avg_rsd:.1f}%
• Maximum Standards RSD: {max_rsd:.1f}%
• Acceptable Threshold: {acceptable_threshold:.1f}% (based on your instrument performance)

Overall Recommendation:
{recommendation}

Quality Criteria Summary:
• R-squared ≥ 0.995: {'✅' if r_squared >= 0.995 else '❌'}
• Recovery 95-105%: {'✅' if all_recoveries_good else '❌'}
• RSD ≤ {acceptable_threshold:.1f}%: {'✅' if precision_good else '❌'}
        """
        
        self.validation_text.setPlainText(validation_text.strip())
    
    def save_calibration(self):
        """Save the custom calibration to file"""
        if not self.calibration_results:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Custom Calibration",
            "custom_calibration.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Prepare save data
                save_data = {
                    'calibration': self.calibration_results,
                    'standards_data': {},
                    'calibration_name': self.calibration_name_edit.text().strip()
                }
                
                # Clean standards data for saving
                for std_name, std_data in self.standards_data.items():
                    save_data['standards_data'][std_name] = {
                        'files': std_data['files'],
                        'intensities': std_data['intensities'],
                        'mean': std_data['mean'],
                        'std': std_data['std'],
                        'rsd': std_data['rsd'],
                        'concentration': std_data['concentration']
                    }
                
                # Convert numpy arrays to lists for JSON serialization
                if 'concentrations' in save_data['calibration']:
                    save_data['calibration']['concentrations'] = save_data['calibration']['concentrations'].tolist()
                if 'intensities' in save_data['calibration']:
                    save_data['calibration']['intensities'] = save_data['calibration']['intensities'].tolist()
                
                # Save to file
                with open(file_path, 'w') as f:
                    json.dump(save_data, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Calibration saved to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error saving calibration: {e}")
    
    def load_calibration(self):
        """Load a custom calibration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Custom Calibration",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    save_data = json.load(f)
                
                # Load calibration results
                self.calibration_results = save_data['calibration']
                
                # Load calibration name if available
                if 'calibration_name' in save_data:
                    self.calibration_name_edit.setText(save_data['calibration_name'])
                    self.calibration_results['name'] = save_data['calibration_name']
                
                # Convert lists back to numpy arrays
                if 'concentrations' in self.calibration_results:
                    self.calibration_results['concentrations'] = np.array(self.calibration_results['concentrations'])
                if 'intensities' in self.calibration_results:
                    self.calibration_results['intensities'] = np.array(self.calibration_results['intensities'])
                
                # Load standards data
                for std_name, std_data in save_data['standards_data'].items():
                    if std_name in self.standards_data:
                        self.standards_data[std_name].update(std_data)
                        self.update_file_list(std_name)
                        self.update_standard_results(std_name)
                
                # Update displays
                self.update_calibration_display()
                self.create_calibration_plot()
                self.perform_validation()
                
                # Enable buttons
                self.save_btn.setEnabled(True)
                self.apply_btn.setEnabled(True)
                self.calc_btn.setEnabled(True)
                
                QMessageBox.information(self, "Success", f"Calibration loaded from {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Error loading calibration: {e}")
    
    def apply_calibration(self):
        """Apply the custom calibration to the main application"""
        if not self.calibration_results:
            return
        
        try:
            # Get the main application
            main_app = self.parent()
            
            # Update the peak fitter in the main application (try both possible names)
            main_fitter = None
            if hasattr(main_app, 'fitter'):
                main_fitter = main_app.fitter
            elif hasattr(main_app, 'peak_fitter'):
                main_fitter = main_app.peak_fitter
            
            if main_fitter:
                # Update the calibration parameters
                main_fitter.calibration_slope = self.calibration_results['slope']
                main_fitter.calibration_intercept = self.calibration_results['intercept']
                main_fitter.calibration_name = self.calibration_results.get('name', 'Custom Calibration')
                
                # Update calibration display in main GUI
                if hasattr(main_app, 'calibration_slope_edit'):
                    main_app.calibration_slope_edit.setText(f"{self.calibration_results['slope']:.2e}")
                if hasattr(main_app, 'calibration_intercept_edit'):
                    main_app.calibration_intercept_edit.setText(f"{self.calibration_results['intercept']:.2f}")
                
                # Recalculate concentrations for existing data with new calibration
                if hasattr(main_app, 'batch_results') and main_app.batch_results:
                    print("Recalculating concentrations with new calibration...")
                    for result in main_app.batch_results:
                        # Recalculate concentration using new calibration
                        new_concentration = main_fitter.apply_calibration(result['integrated_intensity'])
                        result['concentration'] = new_concentration
                    
                    # Recalculate sample groups with new concentrations
                    if hasattr(main_app, 'sample_groups') and main_app.sample_groups:
                        for sample_group in main_app.sample_groups:
                            # Update sample group data with new concentrations
                            updated_data = []
                            for filename, fit_params, intensity, old_conc in sample_group.spectra_data:
                                new_conc = main_fitter.apply_calibration(intensity)
                                updated_data.append((filename, fit_params, intensity, new_conc))
                            
                            # Replace the data and recalculate statistics
                            sample_group.spectra_data = updated_data
                            sample_group.calculate_statistics()
                    
                    # Refresh the plots with new concentrations
                    if hasattr(main_app, 'plot_canvas') and hasattr(main_app, 'sample_groups'):
                        main_app.plot_canvas.plot_sample_statistics(main_app.sample_groups)
                    
                    # Refresh results table display if it exists
                    if hasattr(main_app, 'display_sample_statistics'):
                        main_app.display_sample_statistics(main_app.sample_groups)
                
                # Update single file results if available
                if hasattr(main_app, 'current_data') and main_app.current_data:
                    # Recalculate current file if it exists
                    try:
                        result = main_app.current_data
                        if 'integrated_intensity' in result:
                            new_concentration = main_fitter.apply_calibration(result['integrated_intensity'])
                            result['concentration'] = new_concentration
                            
                            # Update display
                            if hasattr(main_app, 'display_fit_results'):
                                main_app.display_fit_results(
                                    result['fit_params'], 
                                    result['r_squared'], 
                                    result['integrated_intensity'], 
                                    new_concentration
                                )
                    except Exception as e:
                        print(f"Could not update single file results: {e}")
                
                # Update calibration verification plot
                if hasattr(main_app, 'plot_canvas'):
                    # Update the plot title to show custom calibration
                    main_plot = main_app.plot_canvas
                    if hasattr(main_plot, 'ax1') and main_plot.ax1:
                        title = main_plot.ax1.get_title()
                        if "NIST Calibration" in title:
                            new_title = title.replace("NIST Calibration", "Custom Calibration")
                            main_plot.ax1.set_title(new_title)
                            main_plot.draw()
                
                QMessageBox.information(
                    self, 
                    "Applied", 
                    "Custom calibration has been applied to the analysis.\n\n"
                    f"New calibration equation:\n"
                    f"Concentration = {self.calibration_results['slope']:.6f} × Intensity + {self.calibration_results['intercept']:.2f}"
                )
                
                self.accept()
                
            else:
                QMessageBox.warning(self, "Error", "Could not access main application peak fitter.")
                
        except Exception as e:
            QMessageBox.critical(self, "Apply Error", f"Error applying calibration: {e}")


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

def detect_file_format(file_path):
    """
    Detect the format of an XRF data file by examining its content.
    
    Parameters:
    -----------
    file_path : str
        Path to the file to analyze
        
    Returns:
    --------
    format_type : str
        Detected format: 'emsa', 'nist_standard', 'csv', 'excel', 'space_separated', 'tab_separated', 'unknown'
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read first 50 lines to analyze format
            lines = [f.readline().strip() for _ in range(50)]
        
        # Check for EMSA format
        emsa_indicators = ['#FORMAT', '#VERSION', '#SPECTRUM', '#NPOINTS', '#XUNITS']
        if any(indicator in lines[0] for indicator in emsa_indicators):
            return 'emsa'
        
        # Check for NIST standard format
        nist_indicators = ['B-Baseline', 'Spectral	Data	File', 'Data	Starts	Here']
        if any(indicator in ' '.join(lines[:20]) for indicator in nist_indicators):
            return 'nist_standard'
        
        # Find the first non-comment line to analyze format
        data_line = None
        for line in lines:
            if line and not line.startswith('#'):
                data_line = line
                break
        
        if data_line:
            # Check for CSV format (comma-separated)
            if ',' in data_line:
                return 'csv'
            
            # Check for tab-separated format
            if '\t' in data_line:
                return 'tab_separated'
            
            # Check for space-separated format
            if len(data_line.split()) >= 2:
                return 'space_separated'
        
        return 'unknown'
        
    except Exception as e:
        print(f"Error detecting file format for {file_path}: {e}")
        return 'unknown'

def parse_xrf_file_smart(file_path):
    """
    Smart parser for XRF data files that automatically detects and handles various formats.
    
    Parameters:
    -----------
    file_path : str
        Path to the XRF data file
        
    Returns:
    --------
    x : numpy.array
        Energy values (keV)
    y : numpy.array
        Intensity values (counts)
    format_detected : str
        The detected format type
    """
    try:
        # Detect file format
        format_type = detect_file_format(file_path)
        print(f"Detected format for {os.path.basename(file_path)}: {format_type}")
        
        if format_type == 'emsa':
            # Use existing EMSA parser
            metadata, spectrum_df = parse_emsa_file_pandas(file_path)
            if spectrum_df is not None and len(spectrum_df) > 0:
                x = spectrum_df['energy_kev'].values
                y = spectrum_df['counts'].values
                return x, y, format_type
        
        elif format_type == 'nist_standard':
            # Parse NIST standard format with header and 3 columns
            return parse_nist_standard_format(file_path, format_type)
        
        elif format_type == 'csv':
            # Parse CSV format
            return parse_csv_format(file_path, format_type)
        
        elif format_type == 'tab_separated':
            # Parse tab-separated format
            return parse_tab_separated_format(file_path, format_type)
        
        elif format_type == 'space_separated':
            # Parse space-separated format
            return parse_space_separated_format(file_path, format_type)
        
        else:
            # Try fallback parsing methods
            return parse_fallback_format(file_path, format_type)
            
    except Exception as e:
        print(f"Error in smart parsing of {file_path}: {e}")
        return None, None, 'error'

def parse_nist_standard_format(file_path, format_type):
    """Parse NIST standard files with header and 3 columns"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        data_lines = []
        in_data_section = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for data section start
            if "Data Starts Here" in line or "Data	Starts	Here" in line:
                in_data_section = True
                continue
            
            # Parse data lines (should have 3 columns: energy, intensity, baseline)
            if in_data_section:
                # Split by tabs or spaces
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        energy = float(parts[0])
                        intensity = float(parts[1])
                        data_lines.append([energy, intensity])
                    except ValueError:
                        # Skip lines that can't be parsed as numbers
                        continue
        
        if not data_lines:
            raise ValueError("No valid data found in file")
        
        # Convert to numpy arrays
        data_array = np.array(data_lines)
        x = data_array[:, 0]
        y = data_array[:, 1]
        
        return x, y, format_type
        
    except Exception as e:
        print(f"Error parsing NIST standard format {file_path}: {e}")
        return None, None, format_type

def parse_csv_format(file_path, format_type):
    """Parse CSV format files with mixed header and data content"""
    try:
        # Read file line by line to handle mixed content
        data_lines = []
        in_data_section = False
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check for data section start
                if "Data begins below" in line or "Data starts below" in line:
                    in_data_section = True
                    continue
                
                # Parse data lines (should have 2 columns: energy, intensity)
                if in_data_section and not line.startswith('#'):
                    # Split by comma and clean up
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 2:
                        try:
                            energy = float(parts[0])
                            intensity = float(parts[1])
                            data_lines.append([energy, intensity])
                        except ValueError:
                            # Skip lines that can't be parsed as numbers
                            continue
        
        if not data_lines:
            # If no data section found, try to parse the whole file
            try:
                df = pd.read_csv(file_path, header=None)
                
                # Find the first two numeric columns
                numeric_cols = []
                for col in df.columns:
                    if df[col].dtype in ['float64', 'int64'] or df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().any():
                        numeric_cols.append(col)
                        if len(numeric_cols) == 2:
                            break
                
                if len(numeric_cols) >= 2:
                    x = df[numeric_cols[0]].values
                    y = df[numeric_cols[1]].values
                    return x, y, format_type
            except:
                pass
            
            raise ValueError("No valid data found in file")
        
        # Convert to numpy arrays
        data_array = np.array(data_lines)
        x = data_array[:, 0]
        y = data_array[:, 1]
        
        return x, y, format_type
        
    except Exception as e:
        print(f"Error parsing CSV format {file_path}: {e}")
        return None, None, format_type

def parse_tab_separated_format(file_path, format_type):
    """Parse tab-separated format files"""
    try:
        df = pd.read_csv(file_path, delimiter='\t', header=None)
        
        # Find the first two numeric columns
        numeric_cols = []
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64'] or df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().any():
                numeric_cols.append(col)
                if len(numeric_cols) == 2:
                    break
        
        if len(numeric_cols) >= 2:
            x = df[numeric_cols[0]].values
            y = df[numeric_cols[1]].values
            return x, y, format_type
        else:
            raise ValueError("Could not find two numeric columns")
            
    except Exception as e:
        print(f"Error parsing tab-separated format {file_path}: {e}")
        return None, None, format_type

def parse_space_separated_format(file_path, format_type):
    """Parse space-separated format files"""
    try:
        df = pd.read_csv(file_path, delimiter=r'\s+', header=None)
        
        # Find the first two numeric columns
        numeric_cols = []
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64'] or df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().any():
                numeric_cols.append(col)
                if len(numeric_cols) == 2:
                    break
        
        if len(numeric_cols) >= 2:
            x = df[numeric_cols[0]].values
            y = df[numeric_cols[1]].values
            return x, y, format_type
        else:
            raise ValueError("Could not find two numeric columns")
            
    except Exception as e:
        print(f"Error parsing space-separated format {file_path}: {e}")
        return None, None, format_type

def parse_fallback_format(file_path, format_type):
    """Fallback parsing for unknown formats"""
    try:
        # Try multiple parsing strategies
        strategies = [
            lambda: pd.read_csv(file_path, header=None),
            lambda: pd.read_csv(file_path, delimiter='\t', header=None),
            lambda: pd.read_csv(file_path, delimiter=r'\s+', header=None),
            lambda: pd.read_csv(file_path, delimiter=',', header=None)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                df = strategy()
                
                # Find the first two numeric columns
                numeric_cols = []
                for col in df.columns:
                    if df[col].dtype in ['float64', 'int64'] or df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().any():
                        numeric_cols.append(col)
                        if len(numeric_cols) == 2:
                            break
                
                if len(numeric_cols) >= 2:
                    x = df[numeric_cols[0]].values
                    y = df[numeric_cols[1]].values
                    return x, y, f'fallback_{i}'
                    
            except Exception:
                continue
        
        raise ValueError("No parsing strategy worked")
        
    except Exception as e:
        print(f"Error in fallback parsing of {file_path}: {e}")
        return None, None, format_type

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