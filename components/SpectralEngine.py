# class SpectralEngine:
#     samples = {
#         "Reference":(280,50),
#         "Protein":(280,290)
#     }
#     def initialize(self):
#         print("engine initialized")
#     def measure_sample(self, sample_name):
#         return self.samples.get(sample_name,(0,0))
import numpy as np
import math
import json
import time
from datetime import datetime
from enum import Enum

class ScanMode(Enum):
    """Enum for different scanning modes"""
    SINGLE = "single_wavelength"
    SCAN = "full_scan"
    KINETIC = "kinetic"
    TIME_COURSE = "time_course"

class SpectralEngine:
    """Core engine for spectrophotometer operations"""
    
    def __init__(self):
        # Hardware specifications
        self.MIN_WAVELENGTH = 190.0  # nm
        self.MAX_WAVELENGTH = 1100.0  # nm
        self.WAVELENGTH_STEP = 0.1   # nm resolution
        self.ACCURACY = 0.3          # nm accuracy
        
        # Current state
        self.current_wavelength = 450.0  # Default wavelength
        self.target_wavelength = 450.0
        self.is_scanning = False
        self.is_calibrated = False
        self.is_lamp_on = False
        self.sample_present = False
        
        # Data storage
        self.reference_spectrum = {}    # Reference (blank) data
        self.sample_spectrum = {}       # Current sample data
        self.background_spectrum = {}   # Dark current data
        self.calibration_data = {}      # Calibration coefficients
        self.scan_history = []          # History of scans
        self.kinetic_data = []          # Time-course data
        
        # Scan parameters
        self.scan_mode = ScanMode.SINGLE
        self.scan_speed = 1.0  # nm/sec
        self.integration_time = 0.1  # seconds per reading
        self.scan_range = (self.MIN_WAVELENGTH, self.MAX_WAVELENGTH)
        
        # Instrument noise parameters
        self.dark_current = 0.001
        self.readout_noise = 0.005
        self.photometric_noise = 0.01
        
        # Initialize with default calibration
        self._initialize_default_calibration()
        
    def _initialize_default_calibration(self):
        """Initialize with default calibration values"""
        # Polynomial coefficients for wavelength calibration: ax² + bx + c
        self.calibration_data = {
            'wavelength_coeffs': [0.000001, 1.0001, -0.05],  # a, b, c
            'intensity_coeffs': [1.0, 0.0],  # linear correction
            'dark_current': self.dark_current,
            'last_calibration': datetime.now().isoformat(),
            'calibration_valid': False
        }
    
    def initialize(self):
        """Initialize the spectral engine with calibration"""
        print("Spectral Engine: Initializing...")
        self._initialize_default_calibration()
        
        # Set default wavelength to middle of range
        self.current_wavelength = (self.MIN_WAVELENGTH + self.MAX_WAVELENGTH) / 2
        self.target_wavelength = self.current_wavelength
        
        # Perform quick self-test
        print("Spectral Engine: Performing self-test...")
        self_test = self.perform_self_test()
        
        if self_test['passed']:
            print("Spectral Engine: Self-test passed")
            # Turn on lamp by default
            self.is_lamp_on = True
            print("Spectral Engine: Lamp turned on")
        else:
            print("Spectral Engine: Self-test failed - check hardware")
            self.is_lamp_on = False
            
        print(f"Spectral Engine: Ready. Range: {self.MIN_WAVELENGTH}-{self.MAX_WAVELENGTH}nm")
        return self_test['passed']
    
    def set_wavelength(self, wavelength):
        """Set the target wavelength"""
        if not (self.MIN_WAVELENGTH <= wavelength <= self.MAX_WAVELENGTH):
            raise ValueError(
                f"Wavelength {wavelength}nm out of range. "
                f"Valid range: {self.MIN_WAVELENGTH}-{self.MAX_WAVELENGTH}nm"
            )
        
        self.target_wavelength = wavelength
        
        # Simulate wavelength movement
        wavelength_diff = abs(wavelength - self.current_wavelength)
        move_time = wavelength_diff / 10.0  # 10 nm/sec movement speed
        
        # In real hardware, this would control the monochromator
        print(f"Moving from {self.current_wavelength}nm to {wavelength}nm...")
        time.sleep(min(move_time, 0.1))  # Simulated delay
        
        self.current_wavelength = wavelength
        return self.current_wavelength
    
    def goto_wavelength(self, wavelength):
        """Go to specific wavelength (for GOTO button)"""
        return self.set_wavelength(wavelength)
    
    def measure_single(self):
        """Measure intensity at current wavelength"""
        if not self.is_lamp_on:
            raise RuntimeError("Lamp is off. Cannot measure.")
        
        # Apply wavelength calibration
        calibrated_wl = self._apply_wavelength_calibration(self.current_wavelength)
        
        # Simulate photodetector measurement with noise
        intensity = self._simulate_spectral_response(calibrated_wl)
        
        # Apply intensity calibration and add noise
        calibrated_intensity = self._apply_intensity_calibration(intensity)
        noisy_intensity = self._add_measurement_noise(calibrated_intensity)
        
        return {
            'wavelength': self.current_wavelength,
            'calibrated_wavelength': calibrated_wl,
            'intensity': max(0, noisy_intensity),
            'timestamp': datetime.now().isoformat(),
            'sample_present': self.sample_present
        }
    
    def scan_full_range(self, start_wl=None, end_wl=None):
        """Perform a full wavelength scan"""
        if not self.is_lamp_on:
            raise RuntimeError("Lamp is off. Cannot scan.")
        
        start_wl = start_wl if start_wl is not None else self.scan_range[0]
        end_wl = end_wl if end_wl is not None else self.scan_range[1]
        
        if not (self.MIN_WAVELENGTH <= start_wl <= self.MAX_WAVELENGTH):
            raise ValueError(f"Start wavelength {start_wl}nm out of range")
        if not (self.MIN_WAVELENGTH <= end_wl <= self.MAX_WAVELENGTH):
            raise ValueError(f"End wavelength {end_wl}nm out of range")
        if end_wl <= start_wl:
            raise ValueError(f"End wavelength must be greater than start wavelength")
        
        self.is_scanning = True
        scan_data = []
        
        # Calculate number of points
        num_points = int((end_wl - start_wl) / self.WAVELENGTH_STEP) + 1
        
        print(f"Starting scan: {start_wl}-{end_wl}nm ({num_points} points)")
        
        # Simulate scanning each wavelength point
        for i in range(num_points):
            if not self.is_scanning:
                print("Scan stopped by user")
                break
                
            current_wl = start_wl + i * self.WAVELENGTH_STEP
            self.current_wavelength = current_wl
            
            # Measure at this wavelength
            measurement = self.measure_single()
            scan_data.append(measurement)
            
            # Simulate integration time
            time.sleep(self.integration_time)
            
            # Progress indicator
            if i % 100 == 0:
                progress = (i / num_points) * 100
                print(f"Scan progress: {progress:.1f}%")
        
        self.is_scanning = False
        
        # Store the scan
        scan_record = {
            'type': 'full_scan',
            'start_wavelength': start_wl,
            'end_wavelength': end_wl,
            'step_size': self.WAVELENGTH_STEP,
            'data': scan_data,
            'timestamp': datetime.now().isoformat(),
            'sample_present': self.sample_present
        }
        
        self.scan_history.append(scan_record)
        
        # Update sample spectrum
        if self.sample_present:
            self.sample_spectrum = {d['wavelength']: d['intensity'] for d in scan_data}
        
        return scan_record
    
    def measure_absorbance(self):
        """Calculate absorbance from reference and sample measurements"""
        if not self.reference_spectrum:
            raise RuntimeError("No reference spectrum available. Run calibration first.")
        
        if not self.sample_spectrum:
            raise RuntimeError("No sample spectrum available. Scan a sample first.")
        
        absorbance_data = []
        
        # Calculate absorbance for each wavelength point
        for wl, sample_intensity in self.sample_spectrum.items():
            if wl in self.reference_spectrum:
                ref_intensity = self.reference_spectrum[wl]
                
                if ref_intensity > 0:
                    transmittance = sample_intensity / ref_intensity
                    absorbance = -math.log10(transmittance) if transmittance > 0 else float('inf')
                    
                    absorbance_data.append({
                        'wavelength': wl,
                        'absorbance': absorbance,
                        'transmittance': transmittance * 100,  # Percentage
                        'reference_intensity': ref_intensity,
                        'sample_intensity': sample_intensity
                    })
        
        return absorbance_data
    
    def calibrate_reference(self):
        """Calibrate with reference (blank)"""
        print("Starting reference calibration...")
        
        # Store original sample state
        original_sample_state = self.sample_present
        self.sample_present = False
        
        try:
            # Measure dark current first
            self.is_lamp_on = False
            time.sleep(0.1)
            dark_measurement = self.measure_single()
            self.background_spectrum = {self.current_wavelength: dark_measurement['intensity']}
            
            # Turn lamp on and measure reference
            self.is_lamp_on = True
            time.sleep(0.5)  # Lamp warm-up
            
            # Do a quick scan at current wavelength region
            scan_result = self.scan_full_range(
                self.current_wavelength - 5,
                self.current_wavelength + 5
            )
            
            self.reference_spectrum = {d['wavelength']: d['intensity'] for d in scan_result['data']}
            
            # Mark as calibrated
            self.is_calibrated = True
            
            print("Reference calibration complete")
            return True
            
        finally:
            # Restore sample state
            self.sample_present = original_sample_state
    
    def auto_zero(self):
        """Perform auto-zero at current wavelength"""
        print("Performing auto-zero...")
        
        # Measure current intensity
        current_measurement = self.measure_single()
        
        # Store as background for this wavelength
        self.background_spectrum[self.current_wavelength] = current_measurement['intensity']
        
        print(f"Auto-zero complete at {self.current_wavelength}nm")
        return True
    
    def kinetic_scan(self, duration=60, interval=1):
        """Perform kinetic (time-course) measurements"""
        print(f"Starting kinetic scan: {duration} seconds, {interval} second interval")
        
        self.is_scanning = True
        kinetic_data = []
        start_time = time.time()
        measurements_taken = 0
        
        while time.time() - start_time < duration and self.is_scanning:
            measurement = self.measure_single()
            kinetic_data.append({
                'time': measurements_taken * interval,
                'wavelength': measurement['wavelength'],
                'intensity': measurement['intensity'],
                'absorbance': None  # Will calculate later if reference exists
            })
            
            measurements_taken += 1
            time.sleep(interval)
        
        self.is_scanning = False
        
        # Store kinetic data
        self.kinetic_data = kinetic_data
        
        return kinetic_data
    
    def calculate_concentration(self, absorbance, molar_absorptivity=1.0, path_length=1.0):
        """Calculate concentration using Beer-Lambert law"""
        # Beer-Lambert Law: A = ε * c * l
        # A = absorbance, ε = molar absorptivity, c = concentration, l = path length
        
        if path_length <= 0:
            raise ValueError("Path length must be positive")
        
        if molar_absorptivity <= 0:
            raise ValueError("Molar absorptivity must be positive")
        
        concentration = absorbance / (molar_absorptivity * path_length)
        return concentration
    
    def save_data(self, filename):
        """Save current data to file"""
        data_to_save = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'current_wavelength': self.current_wavelength,
                'is_calibrated': self.is_calibrated,
                'sample_present': self.sample_present,
                'instrument': 'Spectrophotometer OS v1.0'
            },
            'reference_spectrum': self.reference_spectrum,
            'sample_spectrum': self.sample_spectrum,
            'background_spectrum': self.background_spectrum,
            'calibration_data': self.calibration_data,
            'recent_scan': self.scan_history[-1] if self.scan_history else None,
            'kinetic_data': self.kinetic_data
        }
        
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        print(f"Data saved to {filename}")
        return True
    
    def load_data(self, filename):
        """Load data from file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Update engine state
        self.reference_spectrum = data.get('reference_spectrum', {})
        self.sample_spectrum = data.get('sample_spectrum', {})
        self.background_spectrum = data.get('background_spectrum', {})
        self.calibration_data = data.get('calibration_data', self.calibration_data)
        
        if 'recent_scan' in data and data['recent_scan']:
            self.scan_history.append(data['recent_scan'])
        
        self.kinetic_data = data.get('kinetic_data', [])
        
        print(f"Data loaded from {filename}")
        return True
    
    def get_status(self):
        """Get current engine status"""
        return {
            'current_wavelength': self.current_wavelength,
            'target_wavelength': self.target_wavelength,
            'is_scanning': self.is_scanning,
            'is_calibrated': self.is_calibrated,
            'is_lamp_on': self.is_lamp_on,
            'sample_present': self.sample_present,
            'scan_mode': self.scan_mode.value,
            'scan_speed': self.scan_speed,
            'integration_time': self.integration_time,
            'has_reference': bool(self.reference_spectrum),
            'has_sample': bool(self.sample_spectrum),
            'scan_history_count': len(self.scan_history),
            'kinetic_data_points': len(self.kinetic_data)
        }
    
    def _simulate_spectral_response(self, wavelength):
        """Simulate the spectral response of the instrument"""
        # Base spectral response curve (simulates lamp emission and detector sensitivity)
        # Gaussian peaks at common lamp lines
        response = 0
        
        # Deuterium lamp continuum + tungsten halogen peaks
        if wavelength < 350:
            # Deuterium UV region
            response = 1000 * math.exp(-0.002 * (wavelength - 250)**2)
        else:
            # Visible/NIR region with tungsten peaks
            response = 800 * math.exp(-0.0001 * (wavelength - 550)**2)
            response += 200 * math.exp(-0.0002 * (wavelength - 750)**2)
            response += 100 * math.exp(-0.0003 * (wavelength - 900)**2)
        
        # Add sample absorption if present
        if self.sample_present:
            # Simulate some absorption peaks
            absorption = 0.8  # Base transmission
            absorption *= (1 - 0.3 * math.exp(-0.001 * (wavelength - 450)**2))  # Peak at 450nm
            absorption *= (1 - 0.5 * math.exp(-0.0005 * (wavelength - 650)**2))  # Peak at 650nm
            response *= absorption
        
        return max(0, response)
    
    def _apply_wavelength_calibration(self, wavelength):
        """Apply wavelength calibration polynomial"""
        a, b, c = self.calibration_data['wavelength_coeffs']
        calibrated = a * wavelength**2 + b * wavelength + c
        return calibrated
    
    def _apply_intensity_calibration(self, intensity):
        """Apply intensity calibration"""
        m, b = self.calibration_data['intensity_coeffs']
        calibrated = m * intensity + b
        return calibrated
    
    def _add_measurement_noise(self, intensity):
        """Add realistic measurement noise"""
        # Dark current noise (Poisson)
        dark_noise = np.random.poisson(self.dark_current * 1000) / 1000
        
        # Readout noise (Gaussian)
        readout_noise = np.random.normal(0, self.readout_noise)
        
        # Photometric noise (proportional to sqrt(intensity))
        if intensity > 0:
            photometric_noise = np.random.normal(0, self.photometric_noise * math.sqrt(intensity))
        else:
            photometric_noise = 0
        
        noisy_intensity = intensity + dark_noise + readout_noise + photometric_noise
        
        return max(0, noisy_intensity)
    
    def perform_self_test(self):
        """Perform instrument self-test"""
        print("Performing self-test...")
        
        tests = {
            'wavelength_range': self._test_wavelength_range(),
            'lamp_function': self._test_lamp(),
            'detector_response': self._test_detector(),
            'communication': self._test_communication(),
            'memory': self._test_memory()
        }
        
        all_passed = all(tests.values())
        
        return {
            'passed': all_passed,
            'tests': tests,
            'timestamp': datetime.now().isoformat()
        }
    
    def _test_wavelength_range(self):
        """Test wavelength range accessibility"""
        try:
            original = self.current_wavelength
            self.set_wavelength(self.MIN_WAVELENGTH)
            self.set_wavelength(self.MAX_WAVELENGTH)
            self.set_wavelength(original)
            return True
        except:
            return False
    
    def _test_lamp(self):
        """Test lamp functionality"""
        try:
            self.is_lamp_on = True
            time.sleep(0.1)
            measurement = self.measure_single()
            self.is_lamp_on = False
            return measurement['intensity'] > 0
        except:
            return False
    
    def _test_detector(self):
        """Test detector response"""
        try:
            # Measure with lamp off (should get low signal)
            self.is_lamp_on = False
            dark_measurement = self.measure_single()
            
            # Measure with lamp on (should get higher signal)
            self.is_lamp_on = True
            time.sleep(0.2)
            light_measurement = self.measure_single()
            self.is_lamp_on = False
            
            return light_measurement['intensity'] > dark_measurement['intensity']
        except:
            return False
    
    def _test_communication(self):
        """Test communication with components"""
        # Simulated test - always passes in software
        return True
    
    def _test_memory(self):
        """Test data storage"""
        try:
            test_data = {'test': 'data'}
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                json.dump(test_data, f)
                temp_file = f.name
            
            with open(temp_file, 'r') as f:
                loaded = json.load(f)
            
            os.unlink(temp_file)
            return loaded == test_data
        except:
            return False