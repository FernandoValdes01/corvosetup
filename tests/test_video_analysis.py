import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("video_analysis", ROOT / "skills/video-editing/scripts/analyze_video.py")
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


class AnalysisParserTests(unittest.TestCase):
    def test_silence_handles_trailing_interval_and_clamps_bounds(self):
        log = 'silence_start: -0.01\nsilence_end: 1.2 | silence_duration: 1.2\nsilence_start: 4.5'
        self.assertEqual(ANALYSIS.silence_intervals(log, 5), [
            {"start": 0.0, "end": 1.2, "duration": 1.2},
            {"start": 4.5, "end": 5, "duration": 0.5}])
        self.assertEqual(ANALYSIS.silence_intervals('silence_end: 1', 5), [])

    def test_all_silent_measurement_is_json_safe(self):
        result = ANALYSIS.loudness_measurement('{"input_i":"-inf","input_tp":"-inf","input_lra":"0.0"}')
        self.assertIsNone(result["integrated_lufs"])
        json.dumps(result, allow_nan=False)
        with self.assertRaises(ValueError):
            ANALYSIS.loudness_measurement('no output')


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe not installed")
class RealMediaAnalysisTests(unittest.TestCase):
    def test_silence_voice_and_loudness_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "voice with spaces.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                            "aevalsrc=if(between(t\\,1\\,2)\\,0.1*sin(440*2*PI*t)\\,0):s=48000:d=3",
                            str(source)], check=True)
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            result = ANALYSIS.analyze(source, minimum=0.5)
            self.assertEqual(len(result["silence_candidates"]), 2)
            self.assertAlmostEqual(result["silence_candidates"][0]["end"], 1, delta=0.02)
            self.assertAlmostEqual(result["silence_candidates"][1]["start"], 2, delta=0.02)
            self.assertTrue(math.isfinite(result["loudness"]["integrated_lufs"]))
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            self.assertEqual(len(list(Path(temp).iterdir())), 1)

    def test_video_without_audio_reports_absence(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "silent.mkv"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                            "color=s=32x32:d=1", "-c:v", "ffv1", str(source)], check=True)
            result = ANALYSIS.analyze(source)
            self.assertIsNone(result["loudness"])
            self.assertEqual(result["silence_candidates"], [])
            with self.assertRaises(ValueError):
                ANALYSIS.analyze(source, noise_db=float('nan'))
