import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from SLinfra.file_logger import FileLogger


def read_log(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_creates_log_dir_and_file(tmp_path):
    log_dir = tmp_path / "logs"
    logger = FileLogger(log_dir=str(log_dir), log_file="app.log")
    logger.info("hello")
    logger.close()

    log_path = log_dir / "app.log"
    assert log_path.exists()
    content = read_log(log_path)
    assert "hello" in content
    assert "[INFO]" in content


def test_level_filtering(tmp_path):
    logger = FileLogger(log_dir=str(tmp_path), log_file="app.log", level="WARNING")
    logger.debug("should not appear")
    logger.info("should not appear either")
    logger.warning("should appear")
    logger.error("should appear too")
    logger.close()

    content = read_log(tmp_path / "app.log")
    assert "should not appear" not in content
    assert "should appear" in content
    assert "should appear too" in content


def test_invalid_level_raises(tmp_path):
    with pytest.raises(ValueError):
        FileLogger(log_dir=str(tmp_path), level="NOT_A_LEVEL")


def test_context_manager_closes_file(tmp_path):
    with FileLogger(log_dir=str(tmp_path)) as logger:
        logger.info("inside context")
    assert logger.file.closed


def test_write_after_close_raises(tmp_path):
    logger = FileLogger(log_dir=str(tmp_path))
    logger.close()
    with pytest.raises(ValueError):
        logger.info("should fail")


def test_double_close_is_safe(tmp_path):
    logger = FileLogger(log_dir=str(tmp_path))
    logger.close()
    logger.close()  # must not raise


def test_rotation_creates_backup_files(tmp_path):
    logger = FileLogger(
        log_dir=str(tmp_path),
        log_file="app.log",
        max_bytes=200,
        backup_count=2,
    )
    for i in range(100):
        logger.info(f"message number {i} padding padding padding")
    logger.close()

    log_dir_files = os.listdir(tmp_path)
    assert "app.log" in log_dir_files
    # At least one rotated backup should exist given the small max_bytes.
    assert any(f.startswith("app.log.") for f in log_dir_files)
    # Never more than backup_count rotated files.
    backups = [f for f in log_dir_files if f.startswith("app.log.")]
    assert len(backups) <= 2


def test_no_rotation_when_max_bytes_zero_or_negative(tmp_path):
    logger = FileLogger(log_dir=str(tmp_path), max_bytes=0)
    for i in range(50):
        logger.info(f"message {i}")
    logger.close()

    log_dir_files = os.listdir(tmp_path)
    backups = [f for f in log_dir_files if f.startswith("app.log.")]
    assert backups == []


def test_concurrent_threads_do_not_interleave_or_crash(tmp_path):
    import threading

    logger = FileLogger(log_dir=str(tmp_path), level="DEBUG")
    errors = []

    def worker(n):
        try:
            for i in range(50):
                logger.info(f"thread-{n}-msg-{i}")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    logger.close()

    assert not errors
    content = read_log(tmp_path / "app.log")
    # Spot check: every line written should be a complete, well-formed line.
    for line in content.splitlines():
        if line.startswith("=== Log started"):
            continue
        assert line.startswith("[")
        assert "] [" in line
