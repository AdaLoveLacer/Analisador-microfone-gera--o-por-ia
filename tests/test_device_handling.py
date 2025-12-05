import pytest

from core.analyzer import MicrophoneAnalyzer


class DummyProcessor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.is_recording = False

    def set_device(self, device_id):
        # simulate device change with no errors
        self.device_id = device_id


def test_set_input_device_noop(monkeypatch, tmp_path):
    analyzer = MicrophoneAnalyzer(config_dir=str(tmp_path), database_dir=str(tmp_path))

    # Inject a dummy processor and override start/stop to avoid real audio
    dummy = DummyProcessor(device_id=1)
    analyzer.audio_processor = dummy

    called = {"stop": 0, "start": 0}

    def fake_stop():
        called["stop"] += 1
        analyzer.is_running = False

    def fake_start():
        called["start"] += 1
        analyzer.is_running = True

    monkeypatch.setattr(analyzer, "stop", fake_stop)
    monkeypatch.setattr(analyzer, "start", fake_start)

    # Ensure analyzer flagged as running
    analyzer.is_running = True

    # Set same device - should be a no-op (no stop/start) but config updated
    analyzer.set_input_device(1, persist=True)

    assert analyzer.audio_processor.device_id == 1
    assert analyzer.config.get("audio.device_id") == 1
    assert analyzer.config.get("audio.input_device") == 1
    assert called["stop"] == 0
    assert called["start"] == 0


def test_set_input_device_restart(monkeypatch, tmp_path):
    analyzer = MicrophoneAnalyzer(config_dir=str(tmp_path), database_dir=str(tmp_path))

    dummy = DummyProcessor(device_id=0)
    analyzer.audio_processor = dummy

    called = {"stop": 0, "start": 0}

    def fake_stop():
        called["stop"] += 1
        analyzer.is_running = False

    def fake_start():
        called["start"] += 1
        analyzer.is_running = True

    monkeypatch.setattr(analyzer, "stop", fake_stop)
    monkeypatch.setattr(analyzer, "start", fake_start)

    analyzer.is_running = True

    # Change to a new device -> should call stop + set_device + start
    analyzer.set_input_device(2, persist=False)

    assert analyzer.audio_processor.device_id == 2
    assert analyzer.config.get("audio.device_id") == 2
    assert analyzer.config.get("audio.input_device") == 2
    assert called["stop"] == 1
    assert called["start"] == 1
