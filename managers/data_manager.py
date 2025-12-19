import json
import os
import shutil
import time
from config import DATA_FILE, BACKUP_FILE

class DataManager:
    def __init__(self):
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    def load(self):
        """Load bingo state. Tries main file, then backup, then returns default."""
        try:
            return self._load_from_file(DATA_FILE)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Main data file missing or corrupt. Trying backup...")
            try:
                return self._load_from_file(BACKUP_FILE)
            except (FileNotFoundError, json.JSONDecodeError):
                print("Backup missing or corrupt. Starting fresh.")
                return self._get_default_state()

    def _load_from_file(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            # basic validation could go here
            return data

    def _get_default_state(self):
        return {
            "history": [],
            "current_number": None,
            "timestamp": time.time(),
            "volume_bgm": 1.0,
            "volume_se": 1.0
        }

    def save(self, history, current_number):
        """Save game state. Preserves other settings."""
        # Load existing to preserve settings
        try:
            state = self._load_from_file(DATA_FILE)
        except:
            state = self._get_default_state()
            
        state["history"] = history
        state["current_number"] = current_number
        state["timestamp"] = time.time()
        
        self._write_to_file(state)

    def save_volume(self, bgm_vol, se_vol):
        """Save volume settings. Preserves game state."""
        try:
            state = self._load_from_file(DATA_FILE)
        except:
            state = self._get_default_state()
            
        state["volume_bgm"] = bgm_vol
        state["volume_se"] = se_vol
        
        self._write_to_file(state)

    def _write_to_file(self, state):
        # 1. Write to main file
        with open(DATA_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # 2. Verify (optional/simple check)
        # 3. Update backup
        try:
            shutil.copy2(DATA_FILE, BACKUP_FILE)
        except: pass
