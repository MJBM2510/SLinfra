import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from SLinfra.state_tracker import StateTracker, Status


def make_tracker(tmp_path, **kwargs):
    return StateTracker(state_file=str(tmp_path / "state.json"), **kwargs)


def test_set_and_get(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("job-1", Status.PENDING.value, retries=0)

    item = tracker.get("job-1")
    assert item["status"] == Status.PENDING.value
    assert item["meta"]["retries"] == 0
    assert "updated_at" in item


def test_get_missing_returns_default(tmp_path):
    tracker = make_tracker(tmp_path)
    assert tracker.get("missing") is None
    assert tracker.get("missing", "fallback") == "fallback"


def test_edit_existing_item(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("job-1", Status.PENDING.value)
    tracker.edit("job-1", Status.DONE.value, result="ok")

    item = tracker.get("job-1")
    assert item["status"] == Status.DONE.value
    assert item["meta"]["result"] == "ok"


def test_edit_missing_item_raises_keyerror(tmp_path):
    tracker = make_tracker(tmp_path)
    with pytest.raises(KeyError):
        tracker.edit("never-set", Status.DONE.value)


def test_remove_existing_and_missing(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("job-1", Status.PENDING.value)
    tracker.remove("job-1")
    assert not tracker.exists("job-1")

    # Removing again must not raise.
    tracker.remove("job-1")


def test_filter_by_status(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("a", Status.DONE.value)
    tracker.set("b", Status.PENDING.value)
    tracker.set("c", Status.DONE.value)

    done = tracker.filter_by_status(Status.DONE.value)
    assert set(done.keys()) == {"a", "c"}


def test_clear(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("a", Status.DONE.value)
    tracker.clear()
    assert tracker.all() == {}


def test_persists_across_instances(tmp_path):
    state_file = tmp_path / "state.json"
    tracker1 = StateTracker(state_file=str(state_file))
    tracker1.set("job-1", Status.PENDING.value)

    tracker2 = StateTracker(state_file=str(state_file))
    assert tracker2.get("job-1")["status"] == Status.PENDING.value


def test_corrupted_state_file_raises_instead_of_silently_clearing(tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError):
        StateTracker(state_file=str(state_file))

    # The corrupted file must be left untouched for inspection.
    assert state_file.read_text(encoding="utf-8") == "{not valid json"


def test_save_is_atomic_no_tmp_file_left_behind(tmp_path):
    tracker = make_tracker(tmp_path)
    tracker.set("a", Status.DONE.value)
    assert not os.path.exists(str(tmp_path / "state.json.tmp"))


def test_concurrent_threads_set_without_losing_updates(tmp_path):
    import threading

    tracker = make_tracker(tmp_path)
    errors = []

    def worker(n):
        try:
            for i in range(20):
                tracker.set(f"job-{n}-{i}", Status.DONE.value)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(tracker.all()) == 100


def test_two_tracker_instances_simulating_separate_processes(tmp_path):
    # Simulates two processes sharing one state file: each holds its own
    # in-memory StateTracker, but the file lock + reload-before-write
    # should stop one from clobbering the other's update.
    state_file = str(tmp_path / "state.json")
    tracker_a = StateTracker(state_file=state_file)
    tracker_b = StateTracker(state_file=state_file)

    tracker_a.set("from-a", Status.DONE.value)
    tracker_b.set("from-b", Status.DONE.value)

    # Reload a fresh tracker to see the true on-disk state.
    final = StateTracker(state_file=state_file)
    assert final.exists("from-a")
    assert final.exists("from-b")


def test_use_file_lock_can_be_disabled(tmp_path):
    tracker = make_tracker(tmp_path, use_file_lock=False)
    tracker.set("a", Status.DONE.value)
    assert tracker.get("a")["status"] == Status.DONE.value
    assert not os.path.exists(str(tmp_path / "state.json.lock"))
