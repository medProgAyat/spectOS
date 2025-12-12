import turtle
from components.Keyboard import Key, KeyType

class SpectrophotometerKeyboard:
    """Main keyboard controller with Turtle visualization"""
    
    def __init__(self, enable_turtle=True):
        self.keys = {}
        self.key_callbacks = {}
        self.enable_turtle = enable_turtle
        self.screen = None
        self.key_layout = []
        
        # Define key positions and types
        self._define_key_layout()
        
        if self.enable_turtle:
            self._setup_turtle()
            self._draw_keyboard()
    
    def _define_key_layout(self):
        """Define the physical layout of keys"""
        # Row 1: Function keys
        self.key_layout.extend([
            ("F1", KeyType.FUNCTION, -200, 150),
            ("F2", KeyType.FUNCTION, -140, 150),
            ("F3", KeyType.FUNCTION, -80, 150),
            ("F4", KeyType.FUNCTION, -20, 150),
            ("F5", KeyType.FUNCTION, 40, 150),
        ])
        
        # Row 2: Numeric keys 7-9 and operations
        self.key_layout.extend([
            ("7", KeyType.NUMERIC, -160, 80),
            ("8", KeyType.NUMERIC, -100, 80),
            ("9", KeyType.NUMERIC, -40, 80),
            ("-", KeyType.OPERATION, 20, 80),
            ("+", KeyType.OPERATION, 80, 80),
        ])
        
        # Row 3: Numeric keys 4-6 and directional
        self.key_layout.extend([
            ("4", KeyType.NUMERIC, -160, 10),
            ("5", KeyType.NUMERIC, -100, 10),
            ("6", KeyType.NUMERIC, -40, 10),
            ("L", KeyType.DIRECTIONAL, 20, 10),  # Left
            ("R", KeyType.DIRECTIONAL, 80, 10),   # Right
        ])
        
        # Row 4: Numeric keys 1-3 and directional
        self.key_layout.extend([
            ("1", KeyType.NUMERIC, -160, -60),
            ("2", KeyType.NUMERIC, -100, -60),
            ("3", KeyType.NUMERIC, -40, -60),
            ("U", KeyType.DIRECTIONAL, 20, -60),  # Up
            ("D", KeyType.DIRECTIONAL, 80, -60),  # Down
        ])
        
        # Row 5: 0, A/Z, S, GOTO, Return
        self.key_layout.extend([
            ("0", KeyType.NUMERIC, -160, -130),
            ("A", KeyType.OPERATION, -100, -130),  # A/Z button
            ("Z", KeyType.OPERATION, -40, -130),   # A/Z button
            ("S", KeyType.SPECIAL, 20, -130),      # Start/Stop
            ("GOTO", KeyType.SPECIAL, 80, -130, 60, 50),  # GOTO lambda
            ("RET", KeyType.SPECIAL, 150, -130, 60, 50),  # Return
        ])
    
    def _setup_turtle(self):
        """Setup turtle graphics window"""
        self.screen = turtle.Screen()
        self.screen.title("Spectrophotometer Keyboard")
        self.screen.setup(width=600, height=400)
        self.screen.bgcolor("#f0f0f0")
        self.screen.tracer(0)  # Turn off animation for