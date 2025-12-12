import threading
import time

class SystemManager:
    def __init__(self):
        self.running = False
        self.components = {}
        self.system_log = []
        self.tasks = []
        self.lock = threading.Lock()
        
    def start(self):
        """Start the system manager"""
        self.running = True
        self.log("System Manager: Starting...")
        
        # Initialize task scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.log("System Manager: Started successfully")
        
    def stop(self):
        """Stop the system manager"""
        self.log("System Manager: Stopping...")
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join(timeout=2)
        self.log("System Manager: Stopped")
        
    def register_component(self, name, component):
        """Register a system component"""
        with self.lock:
            self.components[name] = component
            self.log(f"System Manager: Registered component '{name}'")
            
    def log(self, message):
        """Add a message to system log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.system_log.append(log_entry)
        print(log_entry)
        
        # Keep log size manageable
        if len(self.system_log) > 1000:
            self.system_log = self.system_log[-500:]
            
    def _scheduler_loop(self):
        """Main scheduler loop for system tasks"""
        while self.running:
            with self.lock:
                # Process tasks
                tasks_to_remove = []
                for i, task in enumerate(self.tasks):
                    if task['next_run'] <= time.time():
                        try:
                            task['function'](*task['args'], **task['kwargs'])
                        except Exception as e:
                            self.log(f"Scheduler: Task failed: {e}")
                            
                        if task['interval']:
                            task['next_run'] = time.time() + task['interval']
                        else:
                            tasks_to_remove.append(i)
                            
                # Remove completed one-time tasks
                for i in reversed(tasks_to_remove):
                    self.tasks.pop(i)
                    
            time.sleep(0.1)
            
    def schedule_task(self, func, interval=None, delay=0, *args, **kwargs):
        """Schedule a task to run periodically or once"""
        task = {
            'function': func,
            'interval': interval,
            'next_run': time.time() + delay,
            'args': args,
            'kwargs': kwargs
        }
        
        with self.lock:
            self.tasks.append(task)
            
        self.log(f"Scheduler: Task '{func.__name__}' scheduled")
        
    def get_system_status(self):
        """Get current system status"""
        status = {
            'running': self.running,
            'components': list(self.components.keys()),
            'active_tasks': len(self.tasks),
            'log_entries': len(self.system_log)
        }
        return status