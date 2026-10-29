#!/usr/bin/env python3
"""Read-only media report. Silence intervals are candidates, never editing decisions."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess


def execute(args, timeout=3600):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr[-2000:]}")
    return result


def silence_intervals(log, duration):
    intervals, start = [], None
    events = re.finditer(r"silence_(start|end):\s*([0-9.eE+-]+)", log)
    for event in events:
        kind, value = event.group(1), float(event.group(2))
        value = min(duration, max(0.0, value))
        if kind == "start":
            start = value
        elif start is not None:
            if value > start:
                intervals.append({"start": start, "end": value, "duration": value-start})
            start = None
    if start is not None and start < duration:
        intervals.append({"start": start, "end": duration, "duration": duration-start})
    return intervals


def loudness_measurement(log):
    matches = re.findall(r'\{\s*"input_i"[\s\S]*?\}', log)
    if not matches:
        raise ValueError("FFmpeg did not return a loudness measurement")
    raw = json.loads(matches[-1])
    def finite(key):
        value = float(raw[key])
        return value if math.isfinite(value) else None
    return {"integrated_lufs": finite("input_i"), "true_peak_dbtp": finite("input_tp"),
            "loudness_range_lu": finite("input_lra")}


def analyze(path, noise_db=-35, minimum=0.6, audio_stream=0):
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("Input must be a regular local file")
    if not math.isfinite(noise_db) or not -100 <= noise_db <= 0:
        raise ValueError("noise_db must be between -100 and 0")
    if not math.isfinite(minimum) or minimum <= 0 or audio_stream < 0:
        raise ValueError("minimum must be positive and audio_stream nonnegative")
    probe = json.loads(execute(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                                "-of", "json", str(path)]).stdout)
    duration = float(probe.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("A finite, positive media duration is required")
    audio = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    report = {"input": str(path), "duration_seconds": duration, "streams": probe["streams"],
              "silence_candidates": [], "loudness": None, "warnings": [],
              "detector": {"noise_db": noise_db, "minimum_seconds": minimum,
                           "audio_stream": audio_stream}}
    if not audio:
        report["warnings"].append("No audio stream; no silence or loudness analysis")
        return report
    if audio_stream >= len(audio):
        raise ValueError("Requested audio stream does not exist")
    common = ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-map", f"0:a:{audio_stream}", "-vn"]
    silence = execute(common + ["-af", f"silencedetect=noise={noise_db}dB:d={minimum}", "-f", "null", "-"])
    report["silence_candidates"] = silence_intervals(silence.stderr, duration)
    loudness = execute(common + ["-af", "loudnorm=I=-16:TP=-1:LRA=11:print_format=json", "-f", "null", "-"])
    report["loudness"] = loudness_measurement(loudness.stderr)
    if report["loudness"]["integrated_lufs"] is None:
        report["warnings"].append("No measurable program loudness; inspect silent/very short audio")
    report["warnings"].append("Acoustic silence only: review picture and speech before cutting")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--noise-db", type=float, default=-35)
    parser.add_argument("--min-silence", type=float, default=0.6)
    parser.add_argument("--audio-stream", type=int, default=0, help="Zero-based audio stream to analyze")
    args = parser.parse_args()
    try:
        report = analyze(args.video, args.noise_db, args.min_silence, args.audio_stream)
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Analysis failed: {error}\n")


if __name__ == "__main__":
    main()
