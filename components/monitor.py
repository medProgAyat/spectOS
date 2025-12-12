class Monitor:
    rows = 40
    cols = 80
    
    def __init__(self):
        self.buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.foreground = 'white'
        self.background = 'black'
        
    def getBoundaries(self):
        return (self.cols, self.rows)
    
    def clear(self):
        self.buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0
        
    def write(self, text):
        for char in text:
            if char == '\n':
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.rows:
                    self.scroll()
                    self.cursor_y = self.rows - 1
            else:
                if self.cursor_x >= self.cols:
                    self.cursor_x = 0
                    self.cursor_y += 1
                    if self.cursor_y >= self.rows:
                        self.scroll()
                        self.cursor_y = self.rows - 1
                
                self.buffer[self.cursor_y][self.cursor_x] = char
                self.cursor_x += 1
    
    def scroll(self):
        for i in range(self.rows - 1):
            self.buffer[i] = self.buffer[i + 1].copy()
        self.buffer[self.rows - 1] = [' ' for _ in range(self.cols)]
    
    def get_display(self):
        return [''.join(row) for row in self.buffer]