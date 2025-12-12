#!/usr/bin/env python3
"""
Spectrophotometer OS Kernel
Main entry point for the spectrophotometer operating system
"""

from components.monitor import Monitor
from components.SplashScreen import SplashScreen
from components.SpectralEngine import SpectralEngine
from components.SystemManager import SystemManager
from components.CommandInterface import CommandInterface
from components.SpectrophotometerKeyboard import SpectrophotometerKeyboard
import time

class Kernel:
    def __init__(self):
        self.monitor = Monitor()
        self.splash_screen = SplashScreen()
        self.spectral_engine = SpectralEngine()
        self.system_manager = SystemManager()
        self.keyboard = None
        self.command_interface = None
        
    def initialize_hardware(self):
        """Initialize all hardware components"""
        print("Kernel: Initializing hardware...")
        
        # Initialize monitor
        print(f"Kernel: Monitor initialized ({self.monitor.cols}x{self.monitor.rows})")
        
        # Initialize spectral engine
        engine_initialized = self.spectral_engine.initialize()
        if not engine_initialized:
            print("WARNING: Spectral engine initialization failed")
        
        # Initialize keyboard
        self.keyboard = SpectrophotometerKeyboard(enable_turtle=False)  # Disable turtle for CLI
        
        # Register components with system manager
        self.system_manager.register_component('monitor', self.monitor)
        self.system_manager.register_component('spectral_engine', self.spectral_engine)
        self.system_manager.register_component('keyboard', self.keyboard)
        
        # Initialize command interface
        self.command_interface = CommandInterface(
            self.monitor, 
            self.system_manager, 
            self.spectral_engine,
            self.keyboard
        )
        
        print("Kernel: Hardware initialization complete")
        
    def run(self):
        """Main kernel execution loop"""
        try:
            # Display splash screen
            self.splash_screen.display(self.monitor)
            
            self._refresh_display()
            
            # Start system manager
            self.system_manager.start()
            
            # Display welcome message
            self.monitor.clear()
            welcome_text = [
                "=" * 80,
                "Spectrophotometer OS Kernel - Ready",
                "Type 'help' for available commands",
                "=" * 80,
                "",
                f"Wavelength Range: {self.spectral_engine.MIN_WAVELENGTH}-{self.spectral_engine.MAX_WAVELENGTH}nm",
                f"Current Wavelength: {self.spectral_engine.current_wavelength}nm",
                f"Lamp Status: {'ON' if self.spectral_engine.is_lamp_on else 'OFF'}",
                f"Calibrated: {'YES' if self.spectral_engine.is_calibrated else 'NO'}",
                "",
                "spectro> "
            ]
            
            for line in welcome_text:
                self.monitor.write(line + "\n")
            
            # Main command loop
            while True:
                # Display monitor contents
                self._refresh_display()
                
                # Get command input
                try:
                    command = input().strip()
                    if command.lower() == 'exit':
                        break
                    self.command_interface.process_command(command)
                    self.monitor.write("spectro> ")
                    
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.monitor.write("\nInterrupted. Type 'exit' to quit.\n")
                    self.monitor.write("spectro> ")
                    
        except SystemExit:
            pass
        finally:
            self.shutdown()
            
    def _refresh_display(self):
        """Refresh the display output"""
        print("\033c", end="")  # Clear screen
        for line in self.monitor.get_display():
            print(line)
            
    def shutdown(self):
        """Clean shutdown of the system"""
        print("\nKernel: Shutting down...")
        self.system_manager.stop()
        self.spectral_engine.is_lamp_on = False
        print("Kernel: Shutdown complete")

def main():
    """Main entry point"""
    print("Starting Spectrophotometer OS Kernel...")
    
    # Create and run kernel
    kernel = Kernel()
    
    # Initialize hardware
    kernel.initialize_hardware()
    
    # Run the kernel
    kernel.run()

if __name__ == "__main__":
    main()