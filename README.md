# SLinfra

A lightweight Python utility for file-based logging and persistent state tracking.

## Overview

- SLinfra is a minimal Python package designed to help small to medium projects:
- Keep clean and readable logs
- Persist application state between runs
- Avoid heavy logging frameworks
- It is especially useful for scripts, automation tools, and long-running processes.

---

## Features

- Simple file-based logger
- Persistent state storage (JSON-based)
- Zero external dependencies
- Easy to integrate into existing projects

---

## Installation

```bash
pip install SLinfra
```

---

## Quick Start

### File Logging
```python
from SLinfra.file_logger import FileLogger

logger = FileLogger(log_dir="logs", log_file="app.log")

logger.info("Application started")
logger.warning("Low memory warning")
logger.error("Unexpected error occurred")

logger.close()  # or use it as a context manager, see below
```

This will create (or append to) a log file and store timestamped log messages.
By default the log file rotates at 5 MB, keeping up to 3 backups
(`app.log.1`, `app.log.2`, `app.log.3`); pass `max_bytes=0` to disable
rotation, or tune `max_bytes` / `backup_count` to taste.

Prefer the context manager form so the file handle is always closed:
```python
with FileLogger(log_dir="logs", log_file="app.log") as logger:
    logger.info("Application started")
```

### State Tracking
```python
from SLinfra.state_tracker import StateTracker, Status

state = StateTracker("state.json")

state.set("job-1", Status.PENDING.value, retries=0)
state.edit("job-1", Status.DONE.value, result="ok")

print(state.get("job-1"))
print(state.filter_by_status(Status.DONE.value))
```

This allows your application to persist important values between executions.
Each `set`/`edit`/`remove`/`clear` call saves to disk immediately using an
atomic write (write to a temp file, then `os.replace`), so a crash mid-write
can't leave you with a half-written `state.json`.

By default, `StateTracker` also takes an OS-level advisory file lock
(`fcntl` on POSIX, `msvcrt` on Windows) around each write, so multiple
*processes* pointed at the same state file won't clobber each other's
updates. Pass `use_file_lock=False` if you only ever use one process and
want to skip the lock-file overhead.

---

## Project Structure

```
SLinfra/
├── SLinfra/
│   ├── __init__.py
│   ├── file_logger.py
│   └── state_tracker.py
├── tests/
│   ├── test_file_logger.py
│   └── test_state_tracker.py
├── README.md
├── LICENSE
└── pyproject.toml
```

---

## Design Goals

- Keep the API small and intuitive
- Prefer simplicity over feature overload
- Avoid external dependencies
- Be suitable for educational and practical use

---

## Limitations

- `FileLogger` rotation is size-based only (no time-based rotation, e.g. daily files)
- `StateTracker`'s cross-process lock is advisory: it only protects writers
  that go through `StateTracker` itself, not unrelated programs editing
  the JSON file directly
- Designed for small to medium workloads, not high-throughput logging
  (every write does a `flush()`, so very hot loops will be I/O-bound)

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Roadmap / TODO

- Time-based log rotation (daily/hourly) as an alternative to size-based
- Improve type hints and documentation
- Optional structured (JSON) log output

## License

This project is licensed under the MIT License.