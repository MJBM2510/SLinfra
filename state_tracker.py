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
    
    def save(self):
        tmp_file = self.state + '.tmp'
        
        with open(tmp_file, 'w', encoding = 'utf-8') as file:
            json.dump(self.state, file, ensure_ascii = ascii, indent = 4)
        
        os.replace(tmp_file, self.state_file)
    
    def set(self, item_id, status, **meta):
        
        self.state[item_id] = {
            
            'status': status,
            "updated_at": self._timestamp(),
            "meta": meta
            
        }
        
        self.save()
    
    def get(self, item_id, default = None):
        return self.state.get(item_id, default)