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
            "timestamp": time.time()
        }

    def save(self, history, current_number):
        """Save state to disk with backup protection."""
        state = {
            "history": history,
            "current_number": current_number,
            "timestamp": time.time()
        }
        
        # 1. Write to main file
        with open(DATA_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno()) # Ensure write to disk

        # 2. Verify write (read back)
        try:
            with open(DATA_FILE, 'r') as f:
                json.load(f)
        except Exception as e:
            print(f"Verification failed: {e}")
            return # Don't update backup if main failed

        # 3. Update backup
        shutil.copy2(DATA_FILE, BACKUP_FILE)
