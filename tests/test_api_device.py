import json
import threading

from flask import Flask

from web.app import create_app


class StubConfig:
    def __init__(self):
        self._store = {}

    def set(self, key, value, persist=True):
        self._store[key] = value

    def get(self, key, default=None):
        return self._store.get(key, default)


class StubProcessor:
    def __init__(self, device_id=0):
        self.device_id = device_id

    def list_devices(self):
        return [{"index": self.device_id, "name": "Stub"}]


class StubAnalyzer:
    def __init__(self, device_id=0):
        self.audio_processor = StubProcessor(device_id=device_id)
        self.config = StubConfig()
        self.is_running = True

    def set_input_device(self, device_id, persist=True):
        # Simulate immediate application
        self.config.set("audio.device_id", device_id, persist=persist)
        self.config.set("audio.input_device", device_id, persist=persist)

    def get_status(self):
        return {"is_running": self.is_running}


def test_api_set_device_noop(monkeypatch):
    analyzer = StubAnalyzer(device_id=3)
    app = create_app(analyzer)
    client = app.test_client()

    # Patch analyzer.set_input_device to detect if called
    called = {"count": 0}

    def spy_set_input_device(device_id, persist=True):
        called["count"] += 1

    analyzer.set_input_device = spy_set_input_device

    res = client.post("/api/config/device", data=json.dumps({"device_id": 3}), content_type="application/json")
    assert res.status_code == 200
    body = res.get_json()
    # Current device equal -> should not spawn a set_input_device call
    assert called["count"] == 0
    assert "device_id" not in body or body.get("device_id") == 3


def test_api_set_device_changes(monkeypatch):
    analyzer = StubAnalyzer(device_id=1)
    app = create_app(analyzer)
    client = app.test_client()

    # Replace threading.Thread to run target synchronously for test
    orig_thread = threading.Thread

    class SyncThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=False):
            self._t = target
            self._args = args
            self._kwargs = kwargs or {}

        def start(self):
            # Run synchronously
            if self._t:
                self._t(*self._args, **self._kwargs)

    monkeypatch.setattr(threading, "Thread", SyncThread)

    called = {"count": 0}

    def spy_set_input_device(device_id, persist=True):
        called["count"] += 1
        analyzer.config.set("audio.device_id", device_id, persist=persist)
        analyzer.config.set("audio.input_device", device_id, persist=persist)

    analyzer.set_input_device = spy_set_input_device

    res = client.post("/api/config/device", data=json.dumps({"device_id": 2}), content_type="application/json")
    assert res.status_code == 200
    assert called["count"] == 1
