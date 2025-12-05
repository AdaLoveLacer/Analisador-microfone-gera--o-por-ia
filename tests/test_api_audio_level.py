from web.app import create_app


class FakeProcessor:
    def __init__(self):
        self._q = None
        self.device_id = 0
        self.silence_threshold = 0.02

    def get_energy(self):
        return 0.001

    def is_silent(self):
        return False


class FakeAnalyzer:
    def __init__(self):
        self.audio_processor = FakeProcessor()


def test_audio_level_endpoint(tmp_path):
    analyzer = FakeAnalyzer()
    app = create_app(analyzer)
    client = app.test_client()

    res = client.get('/api/audio/level')
    assert res.status_code == 200
    data = res.get_json()
    assert 'energy' in data
    assert 'db' in data
    assert 'normalized_level' in data
    assert 'is_silent' in data
