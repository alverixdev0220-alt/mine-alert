"""High-quality MP3 pitch shifter (no GUI). Settings are read from settings.txt.

Install:  pip install pedalboard
Run:      python pitch_shift.py [settings.txt]

Uses the Rubber Band library (via pedalboard) with formant preservation,
so raising/lowering pitch keeps the tempo and sounds natural.
"""
import sys
from pathlib import Path

from pedalboard import time_stretch
from pedalboard.io import AudioFile


def load_settings(path):
    cfg = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip().lower()] = value.strip()
    return cfg


def as_bool(value):
    return value.lower() in ("1", "true", "yes", "on")


def shift_file(src, dst, semitones, formants, high_quality, bitrate):
    with AudioFile(str(src)) as f:
        audio = f.read(f.frames)
        sr = f.samplerate
    shifted = time_stretch(
        audio,
        sr,
        stretch_factor=1.0,
        pitch_shift_in_semitones=semitones,
        high_quality=high_quality,
        preserve_formants=formants,
    )
    with AudioFile(str(dst), "w", sr, shifted.shape[0], quality=bitrate) as f:
        f.write(shifted)


def main():
    settings_path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("settings.txt")
    cfg = load_settings(settings_path)

    src = Path(cfg.get("input", "input.mp3"))
    out_dir = Path(cfg.get("output_dir", "output"))
    semitones = float(cfg.get("semitones", "0"))
    formants = as_bool(cfg.get("preserve_formants", "true"))
    high_quality = as_bool(cfg.get("high_quality", "true"))
    bitrate = cfg.get("bitrate", "320k")

    files = sorted(src.glob("*.mp3")) if src.is_dir() else [src]
    if not files:
        sys.exit(f"No MP3 files found at: {src}")

    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{semitones:+g}st"
    for f in files:
        dst = out_dir / f"{f.stem}_{tag}.mp3"
        print(f"{f.name} -> {dst}")
        shift_file(f, dst, semitones, formants, high_quality, bitrate)
    print("Done.")


if __name__ == "__main__":
    main()
