import turtle
import time
from enum import Enum

class KeyType(Enum):
    """Enum for different types of keys"""
    FUNCTION = "FUNCTION"
    NUMERIC = "NUMERIC"
    DIRECTIONAL = "DIRECTIONAL"
    OPERATION = "OPERATION"
    SPECIAL = "SPECIAL"

class Key:
    """Individual key representation"""
    def __init__(self, label, key_type, x, y, width=50, height=50):
        self.label = label
        self.key_type = key_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.turtle = None
        self.callback = None
        self.is_pressed = False
        
        # Colors based on key type
        self.colors = {
            KeyType.FUNCTION: ("#4a86e8", "#1c4587"),  # Blue
            KeyType.NUMERIC: ("#e6b8af", "#a61c00"),   # Red
            KeyType.DIRECTIONAL: ("#b6d7a8", "#38761d"), # Green
            KeyType.OPERATION: ("#f9cb9c", "#e69138"), # Orange
            KeyType.SPECIAL: ("#d9d2e9", "#674ea7")    # Purple
        }
        
    def draw(self, pen):
        """Draw the key using turtle graphics"""
        if self.turtle is None:
            self.turtle = turtle.Turtle()
            self.turtle.hideturtle()
            self.turtle.speed(0)
            self.turtle.penup()
        
        pen = self.turtle
        pen.clear()
        
        # Draw key background
        pen.goto(self.x - self.width/2, self.y - self.height/2)
        pen.fillcolor(self.colors[self.key_type][0])
        pen.begin_fill()
        for _ in range(2):
            pen.forward(self.width)
            pen.left(90)
            pen.forward(self.height)
            pen.left(90)
        pen.end_fill()
        
        # Draw key border
        pen.goto(self.x - self.width/2, self.y - self.height/2)
        pen.pensize(2)
        pen.color(self.colors[self.key_type][1])
        pen.pendown()
        for _ in range(2):
            pen.forward(self.width)
            pen.left(90)
            pen.forward(self.height)
            pen.left(90)
        pen.penup()
        
        # Draw label
        pen.goto(self.x, self.y - 8)
        pen.color("black")
        pen.write(self.label, align="center", font=("Arial", 12, "bold"))
        
        # Draw pressed effect if needed
        if self.is_pressed:
            self._draw_pressed_effect()
    
    def _draw_pressed_effect(self):
        """Draw the key using turtle graphics"""
        if self.turtle is None:
            self.turtle = turtle.Turtle()
            self.turtle.hideturtle()
            self.turtle.speed(0)
            self.turtle.penup()
        """Draw pressed effect on the key"""
        pen = self.turtle
        pen.goto(self.x - self.width/2 + 2, self.y - self.height/2 + 2)
        pen.pensize(1)
        pen.color("#666666")
        pen.pendown()
        for _ in range(2):
            pen.forward(self.width - 4)
            pen.left(90)
            pen.forward(self.height - 4)
            pen.left(90)
        pen.penup()
    
    def set_callback(self, callback):
        """Set callback function for when key is pressed"""
        self.callback = callback
    
    def press(self):
        """Simulate key press"""
        self.is_pressed = True
        self.draw(self.turtle)
        if self.callback:
            self.callback(self.label)
        # Schedule release
        turtle.ontimer(self.release, 200)
    
    def release(self):
        """Release the key"""
        self.is_pressed = False
        self.draw(self.turtle)
    
    def contains_point(self, x, y):
        """Check if point (x,y) is within the key"""
        return (self.x - self.width/2 <= x <= self.x + self.width/2 and
                self.y - self.height/2 <= y <= self.y + self.height/2)