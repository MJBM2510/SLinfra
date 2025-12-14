import os
import json
from datetime import datetime

class StateTracker:
    
    def __init__(self, state_file = 'state.json'):
        
        self.state_file = state_file
        self.state = {}
        self._load
    
    def _load(self):
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding = 'utf-8') as file:
                    self.state = json.load(file)
            except Exception:
                self.state = {}
        else:
            self.state = {}
    
    def _timestamp():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')