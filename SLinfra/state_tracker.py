import os
import json
from datetime import datetime
import threading
from enum import Enum
import sys
import threading
from contextlib import contextmanager

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

class Status(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DONE = "done"
    ERROR = "error"


class StateTracker:

    def __init__(self, state_file="state.json", use_file_lock=True):
        self._lock = threading.RLock()
        self.state_file = state_file
        self.lock_file = state_file + ".lock"
        self.use_file_lock = use_file_lock
        self.state = {}
        self._load()

    @contextmanager
    def _process_lock(self):
        if not self.use_file_lock:
            yield
            return
        
        lock_fd = open(self.lock_file, "a+")
        try:
            if sys.platform == "win32":
                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_LOCK, 1)
            else:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                if sys.platform == "win32":
                    lock_fd.seek(0)
                    msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            finally:
                lock_fd.close()

    def _load(self):
        with self._lock:
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, "r", encoding="utf-8") as file:
                        self.state = json.load(file)
                except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
                    raise ValueError(
                        f"Could not read state file '{self.state_file}': {exc}. "
                        "The file may be corrupted. Inspect or remove it manually "
                        "before continuing -- it was NOT auto-cleared, to avoid "
                        "silent data loss."
                    ) from exc
            else:
                self.state = {}

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _reload_locked(self):
        #Re-read state from disk. Caller must hold both locks.
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as file:
                    self.state = json.load(file)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                # Another writer may be mid-write under normal conditions
                # this shouldn't happen because we hold the process lock,
                # so keep current in-memory state rather than guessing.
                pass

    def _save_locked(self):
        # Write state to disk. Caller must hold both locks.
        tmp_file = self.state_file + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as file:
            json.dump(self.state, file, ensure_ascii=False, indent=4)
        os.replace(tmp_file, self.state_file)

    def save(self):
        with self._lock, self._process_lock():
            self._save_locked()

    def set(self, item_id, status, **meta):
        with self._lock, self._process_lock():
            self._reload_locked()
            self.state[item_id] = {
                "status": status,
                "updated_at": self._timestamp(),
                "meta": meta,
            }
            self._save_locked()

    def get(self, item_id, default=None):
        with self._lock:
            return self.state.get(item_id, default)

    def filter_by_status(self, status):
        with self._lock:
            return {
                key: value
                for key, value in self.state.items()
                if value.get("status") == status
            }

    def remove(self, item_id):
        with self._lock, self._process_lock():
            self._reload_locked()
            if item_id in self.state:
                del self.state[item_id]
                self._save_locked()

    def exists(self, item_id):
        with self._lock:
            return item_id in self.state

    def clear(self):
        with self._lock, self._process_lock():
            self.state = {}
            self._save_locked()

    def all(self):
        with self._lock:
            return dict(self.state)

    def edit(self, item_id, new_status, **new_meta):
        with self._lock, self._process_lock():
            self._reload_locked()
            if item_id not in self.state:
                raise KeyError(
                    f"Cannot edit '{item_id}': it has not been set() yet."
                )
            self.state[item_id]["status"] = new_status
            self.state[item_id]["meta"] = new_meta
            self.state[item_id]["updated_at"] = self._timestamp()
            self._save_locked()