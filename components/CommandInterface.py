class CommandInterface:
    def __init__(self, monitor, system_manager, spectral_engine, keyboard):
        self.monitor = monitor
        self.system_manager = system_manager
        self.spectral_engine = spectral_engine
        self.keyboard = keyboard
        self.commands = {}
        self.register_default_commands()
        
    def register_default_commands(self):
        """Register all available commands"""
        self.commands = {
            'help': self.cmd_help,
            'scan': self.cmd_scan,
            'calibrate': self.cmd_calibrate,
            'status': self.cmd_status,
            'clear': self.cmd_clear,
            'log': self.cmd_log,
            'exit': self.cmd_exit,
            'wavelength': self.cmd_wavelength,
            'wl': self.cmd_wavelength,  # Alias
            'goto': self.cmd_goto,
            'save': self.cmd_save,
            'load': self.cmd_load,
            'lamp': self.cmd_lamp,
            'sample': self.cmd_sample,
            'measure': self.cmd_measure,
            'absorbance': self.cmd_absorbance,
            'concentration': self.cmd_concentration,
            'selftest': self.cmd_selftest,
            'autozero': self.cmd_autozero,
            'kinetic': self.cmd_kinetic
        }
        
    def process_command(self, command_line):
        """Process a command line input"""
        parts = command_line.strip().split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.monitor.write(f"Error executing command: {e}\n")
        else:
            self.monitor.write(f"Unknown command: {cmd}. Type 'help' for available commands.\n")
            
    def cmd_help(self, args):
        """Display help information"""
        help_text = """
=== Spectrophotometer OS Commands ===

Measurement Commands:
  measure                - Measure intensity at current wavelength
  scan [start] [end]    - Perform full wavelength scan (default: 400-700nm)
  kinetic [time] [int]  - Time-course measurements (default: 60s, 1s interval)
  absorbance            - Calculate absorbance from reference & sample
  concentration [abs]   - Calculate concentration from absorbance

Wavelength Control:
  wavelength [nm]       - Set/get current wavelength (alias: wl)
  goto [nm]             - Go to specific wavelength
  autozero              - Perform auto-zero at current wavelength

System Control:
  lamp [on|off]         - Turn lamp on/off
  sample [present|absent] - Set sample presence
  calibrate             - Calibrate with reference (blank)
  selftest              - Perform instrument self-test

Data Management:
  save <filename>       - Save current data to file
  load <filename>       - Load data from file

Utility Commands:
  status                - Display system status
  clear                 - Clear the screen
  log [n]               - Show last n log entries (default: 10)
  exit                  - Exit the application
  help                  - Display this help message

Keyboard Simulation:
  Press corresponding keys to simulate hardware buttons
  F1-F5, 0-9, +, -, L, R, U, D, S, A, Z, GOTO, RET
"""
        self.monitor.write(help_text)
        
    def cmd_scan(self, args):
        """Perform a spectral scan"""
        # Default scan range
        start_wl = 400.0
        end_wl = 700.0
        
        if len(args) >= 1:
            try:
                start_wl = float(args[0])
            except ValueError:
                self.monitor.write(f"Invalid start wavelength: {args[0]}\n")
                return
                
        if len(args) >= 2:
            try:
                end_wl = float(args[1])
            except ValueError:
                self.monitor.write(f"Invalid end wavelength: {args[1]}\n")
                return
        
        sample_name = "Sample_1"
        if len(args) >= 3:
            sample_name = args[2]
            
        self.monitor.write(f"Starting scan of '{sample_name}' from {start_wl}nm to {end_wl}nm...\n")
        
        try:
            scan_result = self.spectral_engine.scan_full_range(start_wl, end_wl)
            
            # Display summary
            if scan_result['data']:
                intensities = [d['intensity'] for d in scan_result['data']]
                wavelengths = [d['wavelength'] for d in scan_result['data']]
                
                max_idx = intensities.index(max(intensities))
                min_idx = intensities.index(min(intensities))
                
                self.monitor.write(f"Scan complete: {len(scan_result['data'])} data points\n")
                self.monitor.write(f"Peak intensity: {intensities[max_idx]:.2f} at {wavelengths[max_idx]}nm\n")
                self.monitor.write(f"Min intensity: {intensities[min_idx]:.2f} at {wavelengths[min_idx]}nm\n")
                self.monitor.write(f"Scan saved to history (ID: {len(self.spectral_engine.scan_history)})\n")
        except Exception as e:
            self.monitor.write(f"Scan failed: {e}\n")
            
    def cmd_calibrate(self, args):
        """Perform calibration"""
        self.monitor.write("Starting calibration procedure...\n")
        
        try:
            if self.spectral_engine.calibrate_reference():
                self.monitor.write("Calibration successful. Reference spectrum saved.\n")
            else:
                self.monitor.write("Calibration failed.\n")
        except Exception as e:
            self.monitor.write(f"Calibration error: {e}\n")
            
    def cmd_status(self, args):
        """Display system status"""
        status = self.system_manager.get_system_status()
        engine_status = self.spectral_engine.get_status()
        
        self.monitor.write("=== System Status ===\n")
        self.monitor.write(f"System Running: {status['running']}\n")
        self.monitor.write(f"Active Components: {', '.join(status['components'])}\n")
        self.monitor.write(f"Active Tasks: {status['active_tasks']}\n")
        self.monitor.write(f"Log Entries: {status['log_entries']}\n")
        
        self.monitor.write("\n=== Spectrometer Status ===\n")
        self.monitor.write(f"Current Wavelength: {engine_status['current_wavelength']}nm\n")
        self.monitor.write(f"Lamp: {'ON' if engine_status['is_lamp_on'] else 'OFF'}\n")
        self.monitor.write(f"Calibrated: {'YES' if engine_status['is_calibrated'] else 'NO'}\n")
        self.monitor.write(f"Scanning: {'YES' if engine_status['is_scanning'] else 'NO'}\n")
        self.monitor.write(f"Sample Present: {'YES' if engine_status['sample_present'] else 'NO'}\n")
        self.monitor.write(f"Scan Mode: {engine_status['scan_mode']}\n")
        self.monitor.write(f"Scans in History: {engine_status['scan_history_count']}\n")
        self.monitor.write("====================\n")
        
    def cmd_clear(self, args):
        """Clear the screen"""
        self.monitor.clear()
        
    def cmd_log(self, args):
        """Display system log"""
        try:
            n = int(args[0]) if args else 10
        except ValueError:
            n = 10
            
        logs = self.system_manager.system_log[-n:]
        self.monitor.write(f"=== Last {len(logs)} Log Entries ===\n")
        for log in logs:
            self.monitor.write(log + "\n")
        self.monitor.write("=============================\n")
        
    def cmd_wavelength(self, args):
        """Set or get current wavelength"""
        if args:
            try:
                wl = float(args[0])
                actual_wl = self.spectral_engine.set_wavelength(wl)
                self.monitor.write(f"Wavelength set to {actual_wl}nm\n")
            except ValueError as e:
                self.monitor.write(f"Error: {e}\n")
        else:
            self.monitor.write(f"Current wavelength: {self.spectral_engine.current_wavelength}nm\n")
            
    def cmd_goto(self, args):
        """Go to specific wavelength"""
        if not args:
            self.monitor.write("Usage: goto <wavelength>\n")
            return
            
        try:
            wl = float(args[0])
            actual_wl = self.spectral_engine.goto_wavelength(wl)
            self.monitor.write(f"GOTO wavelength: {actual_wl}nm\n")
        except ValueError as e:
            self.monitor.write(f"Error: {e}\n")
            
    def cmd_lamp(self, args):
        """Control lamp"""
        if args:
            state = args[0].lower()
            if state in ['on', '1', 'true']:
                self.spectral_engine.is_lamp_on = True
                self.monitor.write("Lamp turned ON\n")
            elif state in ['off', '0', 'false']:
                self.spectral_engine.is_lamp_on = False
                self.monitor.write("Lamp turned OFF\n")
            else:
                self.monitor.write("Usage: lamp [on|off]\n")
        else:
            state = "ON" if self.spectral_engine.is_lamp_on else "OFF"
            self.monitor.write(f"Lamp is {state}\n")
            
    def cmd_sample(self, args):
        """Set sample presence"""
        if args:
            state = args[0].lower()
            if state in ['present', 'yes', 'true', '1']:
                self.spectral_engine.sample_present = True
                self.monitor.write("Sample set as PRESENT\n")
            elif state in ['absent', 'no', 'false', '0', 'blank']:
                self.spectral_engine.sample_present = False
                self.monitor.write("Sample set as ABSENT (blank)\n")
            else:
                self.monitor.write("Usage: sample [present|absent]\n")
        else:
            state = "PRESENT" if self.spectral_engine.sample_present else "ABSENT"
            self.monitor.write(f"Sample is {state}\n")
            
    def cmd_measure(self, args):
        """Measure intensity at current wavelength"""
        try:
            measurement = self.spectral_engine.measure_single()
            self.monitor.write(f"Measurement at {measurement['wavelength']}nm:\n")
            self.monitor.write(f"  Intensity: {measurement['intensity']:.2f}\n")
            self.monitor.write(f"  Sample: {'Present' if measurement['sample_present'] else 'Absent'}\n")
            self.monitor.write(f"  Time: {measurement['timestamp']}\n")
        except Exception as e:
            self.monitor.write(f"Measurement failed: {e}\n")
            
    def cmd_absorbance(self, args):
        """Calculate absorbance"""
        try:
            absorbance_data = self.spectral_engine.measure_absorbance()
            if absorbance_data:
                self.monitor.write(f"Absorbance calculated for {len(absorbance_data)} wavelengths\n")
                
                # Show first few values
                for i, data in enumerate(absorbance_data[:5]):
                    self.monitor.write(
                        f"  {data['wavelength']}nm: "
                        f"A={data['absorbance']:.3f}, "
                        f"T={data['transmittance']:.1f}%\n"
                    )
                
                if len(absorbance_data) > 5:
                    self.monitor.write(f"  ... and {len(absorbance_data) - 5} more wavelengths\n")
            else:
                self.monitor.write("No absorbance data available. Need reference and sample spectra.\n")
        except Exception as e:
            self.monitor.write(f"Absorbance calculation failed: {e}\n")
            
    def cmd_concentration(self, args):
        """Calculate concentration"""
        if not args:
            self.monitor.write("Usage: concentration <absorbance> [molar_absorptivity] [path_length]\n")
            return
            
        try:
            absorbance = float(args[0])
            molar_absorptivity = float(args[1]) if len(args) > 1 else 1.0
            path_length = float(args[2]) if len(args) > 2 else 1.0
            
            concentration = self.spectral_engine.calculate_concentration(
                absorbance, molar_absorptivity, path_length
            )
            
            self.monitor.write(f"Beer-Lambert Law Calculation:\n")
            self.monitor.write(f"  Absorbance (A): {absorbance:.3f}\n")
            self.monitor.write(f"  Molar Absorptivity (ε): {molar_absorptivity} L·mol⁻¹·cm⁻¹\n")
            self.monitor.write(f"  Path Length (l): {path_length} cm\n")
            self.monitor.write(f"  Concentration (c): {concentration:.4f} mol/L\n")
            self.monitor.write(f"                    = {concentration*1000:.2f} mmol/L\n")
            
        except ValueError as e:
            self.monitor.write(f"Invalid input: {e}\n")
            
    def cmd_selftest(self, args):
        """Perform self-test"""
        self.monitor.write("Performing instrument self-test...\n")
        
        try:
            self_test = self.spectral_engine.perform_self_test()
            
            self.monitor.write(f"Self-test result: {'PASS' if self_test['passed'] else 'FAIL'}\n")
            for test_name, result in self_test['tests'].items():
                status = "PASS" if result else "FAIL"
                self.monitor.write(f"  {test_name}: {status}\n")
                
        except Exception as e:
            self.monitor.write(f"Self-test failed: {e}\n")
            
    def cmd_autozero(self, args):
        """Perform auto-zero"""
        self.monitor.write("Performing auto-zero...\n")
        
        try:
            if self.spectral_engine.auto_zero():
                self.monitor.write(f"Auto-zero complete at {self.spectral_engine.current_wavelength}nm\n")
        except Exception as e:
            self.monitor.write(f"Auto-zero failed: {e}\n")
            
    def cmd_kinetic(self, args):
        """Perform kinetic scan"""
        duration = 60.0
        interval = 1.0
        
        if len(args) >= 1:
            try:
                duration = float(args[0])
            except ValueError:
                self.monitor.write(f"Invalid duration: {args[0]}\n")
                return
                
        if len(args) >= 2:
            try:
                interval = float(args[1])
            except ValueError:
                self.monitor.write(f"Invalid interval: {args[1]}\n")
                return
        
        self.monitor.write(f"Starting kinetic scan: {duration} seconds, {interval} second interval\n")
        
        try:
            kinetic_data = self.spectral_engine.kinetic_scan(duration, interval)
            self.monitor.write(f"Kinetic scan complete: {len(kinetic_data)} data points\n")
            
            if kinetic_data:
                first = kinetic_data[0]
                last = kinetic_data[-1]
                self.monitor.write(f"  First: {first['intensity']:.2f} at {first['time']}s\n")
                self.monitor.write(f"  Last: {last['intensity']:.2f} at {last['time']}s\n")
                
        except Exception as e:
            self.monitor.write(f"Kinetic scan failed: {e}\n")
            
    def cmd_save(self, args):
        """Save spectrum data"""
        if not args:
            self.monitor.write("Usage: save <filename>\n")
            return
            
        filename = args[0]
        if not filename.endswith('.json'):
            filename += '.json'
            
        self.monitor.write(f"Saving data to {filename}...\n")
        
        try:
            if self.spectral_engine.save_data(filename):
                self.monitor.write(f"Data saved successfully to {filename}\n")
        except Exception as e:
            self.monitor.write(f"Save failed: {e}\n")
            
    def cmd_load(self, args):
        """Load data from file"""
        if not args:
            self.monitor.write("Usage: load <filename>\n")
            return
            
        filename = args[0]
        self.monitor.write(f"Loading data from {filename}...\n")
        
        try:
            if self.spectral_engine.load_data(filename):
                self.monitor.write(f"Data loaded successfully from {filename}\n")
        except Exception as e:
            self.monitor.write(f"Load failed: {e}\n")
            
    def cmd_exit(self, args):
        """Exit the application"""
        self.monitor.write("Shutting down system...\n")
        self.system_manager.stop()
        raise SystemExit