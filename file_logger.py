import os
from datetime import datetime


class FileLogger:

    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}

    def __init__(self, log_dir="logs", log_file="app.log", level="INFO"):
        self.level = self.LEVELS.get(level, 20)
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, log_file)

        self._prepare_environment()
        self.file = open(self.log_path, "a", encoding="utf-8")

    def _prepare_environment(self):
        os.makedirs(self.log_dir, exist_ok=True)

        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as file:
                file.write(f"=== Log started at {self._timestamp()} ===\n")

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write(self, level, message):
        if self.LEVELS[level] < self.level:
            return

        line = f"[{self._timestamp()}] [{level}] | {message}"
        self.file.write(line + "\n")
        self.file.flush()

    def info(self, message):
        self._write("INFO", message)

    def warning(self, message):
        self._write("WARNING", message)

    def error(self, message):
        self._write("ERROR", message)

    def debug(self, message):
        self._write("DEBUG", message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if not self.file.closed:
            self.file.close()


# test
if __name__ == "__main__":
    with FileLogger(level="DEBUG") as logger:
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
