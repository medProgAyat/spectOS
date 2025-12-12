class PreservedPage:
    def __init__(self):
        self.content = []
        self.cursor_position = (0, 0)
        self.display_attributes = {}
        
    def save_state(self, monitor):
        """Save the current monitor state"""
        self.content = monitor.get_display()
        self.cursor_position = (monitor.cursor_x, monitor.cursor_y)
        self.display_attributes = {
            'foreground': monitor.foreground,
            'background': monitor.background
        }
        
    def restore_state(self, monitor):
        """Restore the saved state to monitor"""
        monitor.clear()
        for i, line in enumerate(self.content):
            if i < monitor.rows:
                monitor.cursor_y = i
                monitor.cursor_x = 0
                monitor.write(line)
        
        monitor.cursor_x, monitor.cursor_y = self.cursor_position
        monitor.foreground = self.display_attributes.get('foreground', 'white')
        monitor.background = self.display_attributes.get('background', 'black')