import numpy as np
from core.analyzer import MicrophoneAnalyzer


def test_autotune_applies_gain(tmp_path):
    analyzer = MicrophoneAnalyzer(config_dir=str(tmp_path), database_dir=str(tmp_path))

    # Prepare a very low amplitude signal (should be boosted)
    low_signal = np.ones(1600, dtype=np.float32) * 1e-4

    # Ensure auto gain enabled and a reasonable target
    analyzer.config.set("audio.auto_gain_enabled", True, persist=False)
    analyzer.config.set("audio.target_db", -20.0, persist=False)
    analyzer.config.set("audio.max_gain_db", 40.0, persist=False)

    out = analyzer._prepare_audio_for_transcription(low_signal, 16000)

    # RMS should increase
    rms_in = float(np.sqrt(np.mean(low_signal ** 2)))
    rms_out = float(np.sqrt(np.mean(out ** 2)))
    assert rms_out > rms_in
