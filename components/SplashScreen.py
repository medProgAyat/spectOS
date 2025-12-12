from components.PreservedPage import PreservedPage
import time

class SplashScreen(PreservedPage):
    def __init__(self):
        super().__init__()
        self.show_time = 2.0  # seconds
        self.splash_text = [
            "╔══════════════════════════════════════════════════════════════════════════════╗",
            "║                                                                              ║",
            "║                    SPECTROPHOTOMETER OS KERNEL v1.0                          ║",
            "║                                                                              ║",
            "║                          Spectral Analysis System                            ║",
            "║                                                                              ║",
            "║         Wavelength Range: 190nm - 1100nm                                     ║",
            "║         Resolution: 0.1nm                                                    ║",
            "║         Accuracy: ±0.3nm                                                     ║",
            "║                                                                              ║",
            "║                                                                              ║",
            "║         Initializing hardware components...                                  ║",
            "║         • Monochromator      [✓]                                             ║",
            "║         • Photodetector      [✓]                                             ║",
            "║         • Light Source       [✓]                                             ║",
            "║         • Sample Chamber     [✓]                                             ║",
            "║         • Thermal Control    [✓]                                             ║",
            "║                                                                              ║",
            "║                                                                              ║",
            "║         Loading calibration data...                                          ║",
            "║         Starting spectral engine...                                          ║",
            "║                                                                              ║",
            "║                                                                              ║",
            "║                                                                              ║",
            "║         Copyright © 2024 Spectral Systems Inc.                               ║",
            "║         All Rights Reserved                                                  ║",
            "║                                                                              ║",
            "╚══════════════════════════════════════════════════════════════════════════════╝"
        ]
        
    def display(self, monitor):
        """Display the splash screen"""
        monitor.clear()
        monitor.foreground = 'cyan'
        
        # Center the splash text
        start_y = max(0, (monitor.rows - len(self.splash_text)) // 2)
        
        for i, line in enumerate(self.splash_text):
            if i + start_y < monitor.rows:
                monitor.cursor_y = i + start_y
                monitor.cursor_x = max(0, (monitor.cols - len(line)) // 2)
                monitor.write(line)
        
        # Add progress indicator
        monitor.cursor_y = monitor.rows - 3
        monitor.cursor_x = monitor.cols // 2 - 10
        monitor.write("[" + " " * 20 + "]")
        
        # Animate progress bar
        for i in range(21):
            time.sleep(self.show_time / 21)
            monitor.cursor_y = monitor.rows - 3
            monitor.cursor_x = monitor.cols // 2 - 9 + i
            monitor.write("█")
            
        time.sleep(5)
        
        # Save the splash screen state
        self.save_state(monitor)