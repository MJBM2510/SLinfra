import os
import json
from datetime import datetime

class StateTracker:
    
    def __init__(self, state_file = 'state.json'):
        
        self.state_file = state_file
        self.state = {}
        self._load()
    
    def _load(self):
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding = 'utf-8') as file:
                    self.state = json.load(file)
            except Exception:
                self.state = {}
        else:
            self.state = {}
    
    def _timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def save(self):
        tmp_file = self.state_file + '.tmp'
        
        with open(tmp_file, 'w', encoding = 'utf-8') as file:
            json.dump(self.state, file, ensure_ascii = False, indent = 4)
        
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
    
    def filter_by_status(self, status):

        return { 
            key: value for key, value in self.state.items() 
            if value.get('status') == status
        }
    
    def remove(self, item_id):
        
        if item_id in self.state:
            del self.state[item_id]
            self.save()
    
    def exists(self, item_id):
        return item_id in self.state
    
    def clear(self):
        self.state = {}
        self.save()
    
    def all(self):
        return self.state
