import os
from datetime import datetime

class FileLogger:
    
    LEVELS= {
        
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40
        
    }
    
    def __init__(self, log_dir = 'logs', log_file = 'app.log', level = 'INFO'):
        
        self.level = self.LEVELS.get(level, 20)
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, log_file)
        
        self._prepare_evnironment()
        self.file = open(self.log_path, 'a', encoding = 'utf-8')
    
    def _prepare_evnironment(self):
        
        os.makedirs(self.log_dir, exist_ok = True)
        
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', encoding = 'utf-8') as file:
                file.write(f"=== Log started at {self._timestamp()} ===\n")
    
    def _timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _write(self, level, message):
        
        if self.LEVELS[level] < self.level:
            return
        
        line = f'[{self._timestamp()}] [{level}] | {message}'
        self.file.write(line + '\n')
        self.file.flush()