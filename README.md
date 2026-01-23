# infra

A lightweight Python utility for file-based logging and persistent state tracking.

## Overview

- infra is a minimal Python package designed to help small to medium projects:
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
pip install infra
```

---

## Quick Start

### File Logging
```python
from infra.file_logger import FileLogger

logger = FileLogger("app.log")

logger.info("Application started")
logger.warning("Low memory warning")
logger.error("Unexpected error occurred")
```

This will create (or append to) a log file and store timestamped log messages.

### State Tracking
```python
from infra.state_tracker import StateTracker

state = StateTracker("state.json")

state["last_run"] = "2026-01-23T14:00"
state["counter"] = 5
state.save()
```

This allows your application to persist important values between executions.

---

## Project Structure

```
infra/
├── infra/
│   ├── __init__.py
│   ├── file_logger.py
│   └── state_tracker.py
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

- Not thread-safe
- No log rotation support
- Designed for small to medium workloads

---

## Roadmap / TODO

- Add unit tests
- Add log rotation support
- Improve type hints and documentation

## License

This project is licensed under the MIT License.
