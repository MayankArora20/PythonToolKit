#!/usr/bin/env python3
"""Report likely duplicate media files across two folders.

Output format per line:
    file1Path|file2Path|reason

The script compares files by:
- fuzzy/similar names (not strict pattern matching)
- same or similar media type
- similar size
- audio quality (bitrate/sample rate)
- image quality (resolution)

No deletion is performed. This is a reporting-only tool.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm"}


def normalize_name(name: str) -> str:
    clean = Path(name).stem.lower()
    clean = re.sub(r"[_\-\.]+", " ", clean)
    clean = re.sub(r"[^a-z0-9 ]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def name_similarity(a: Path, b: Path) -> float:
    left = normalize_name(a.name)
    right = normalize_name(b.name)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def file_extension_group(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "other"


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024 or unit == "GB":
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} GB"


def safe_percent_difference(a: int, b: int) -> float:
    if a <= 0 or b <= 0:
        return 0.0
    return abs(a - b) / max(a, b)


def maybe_read_image_resolution(path: Path) -> Dict[str, int]:
    try:
        from PIL import Image

        with Image.open(path) as img:
            return {"width": img.width, "height": img.height}
    except Exception:
        return {}


def maybe_read_audio_quality(path: Path) -> Dict[str, float]:
    info: Dict[str, float] = {}

    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(path, easy=True)
        if audio is not None:
            if hasattr(audio, "info") and audio.info is not None:
                info["bitrate"] = float(getattr(audio.info, "bitrate", 0) or 0)
                info["sample_rate"] = float(getattr(audio.info, "sample_rate", 0) or 0)
                info["duration"] = float(getattr(audio.info, "length", 0) or 0)
            return info
    except Exception:
        pass

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            payload = json.loads(result.stdout)
            streams = payload.get("streams", [])
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
            fmt = payload.get("format", {})
            bitrate = audio_stream.get("bit_rate") or fmt.get("bit_rate")
            sr = audio_stream.get("sample_rate")
            duration = fmt.get("duration")
            if bitrate:
                info["bitrate"] = float(bitrate)
            if sr:
                info["sample_rate"] = float(sr)
            if duration:
                info["duration"] = float(duration)
            return info
    except Exception:
        pass

    return info


def get_media_quality(path: Path) -> Dict[str, float]:
    ext = path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return maybe_read_audio_quality(path)
    if ext in IMAGE_EXTENSIONS:
        data = maybe_read_image_resolution(path)
        return {"width": float(data.get("width", 0) or 0), "height": float(data.get("height", 0) or 0)}
    return {}


def scan_files(folder: str) -> List[Path]:
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    files: List[Path] = []
    for path in root.rglob("*"):
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.name.lower())


def is_candidate_pair(file1: Path, file2: Path, min_name_score: float) -> bool:
    same_type = file_extension_group(file1) == file_extension_group(file2)
    if not same_type:
        return False

    name_score = name_similarity(file1, file2)
    if name_score >= min_name_score:
        return True

    if file1.name.lower() == file2.name.lower():
        return True

    return False


def build_reason(file1: Path, file2: Path) -> str:
    reasons: List[str] = []
    name_score = name_similarity(file1, file2)
    reasons.append(f"name_score={name_score:.2f}")

    group1 = file_extension_group(file1)
    group2 = file_extension_group(file2)
    if group1 == group2:
        reasons.append(f"type={group1}")

    size1 = file1.stat().st_size
    size2 = file2.stat().st_size
    size_diff = safe_percent_difference(size1, size2)
    if size_diff <= 0.15:
        reasons.append(f"size_close={size_diff:.2%}")
    else:
        reasons.append(f"size_diff={size_diff:.2%}")

    q1 = get_media_quality(file1)
    q2 = get_media_quality(file2)

    if group1 == "audio" and group2 == "audio":
        br1 = q1.get("bitrate")
        br2 = q2.get("bitrate")
        sr1 = q1.get("sample_rate")
        sr2 = q2.get("sample_rate")
        if br1 and br2:
            reasons.append(f"bitrate={int(br1)} vs {int(br2)}")
        if sr1 and sr2:
            reasons.append(f"sample_rate={int(sr1)} vs {int(sr2)}")

    if group1 == "image" and group2 == "image":
        w1 = q1.get("width")
        h1 = q1.get("height")
        w2 = q2.get("width")
        h2 = q2.get("height")
        if w1 and w2 and h1 and h2:
            reasons.append(f"resolution={int(w1)}x{int(h1)} vs {int(w2)}x{int(h2)}")

    return "; ".join(reasons)


def compare_folders(folder1: str, folder2: str, min_name_score: float = 0.75) -> List[str]:
    files1 = scan_files(folder1)
    files2 = scan_files(folder2)
    report_lines: List[str] = []

    for file1 in files1:
        for file2 in files2:
            if not is_candidate_pair(file1, file2, min_name_score):
                continue

            reason = build_reason(file1, file2)
            report_lines.append(f"{file1}|{file2}|{reason}")

    return sorted(set(report_lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Report likely duplicate media files between two folders.")
    parser.add_argument("folder1", help="First folder to scan")
    parser.add_argument("folder2", help="Second folder to scan")
    parser.add_argument("--report", help="Optional path for the report output file")
    parser.add_argument("--min-name-score", type=float, default=0.75, help="Fuzzy name similarity threshold (0.0-1.0). Default: 0.75")
    args = parser.parse_args()

    try:
        report_lines = compare_folders(args.folder1, args.folder2, min_name_score=args.min_name_score)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(report_lines) + ("\n" if report_lines else ""), encoding="utf-8")

    if not report_lines:
        print("No likely duplicate candidates were found.")
        if args.report:
            print(f"Report file written: {args.report}")
        return 0

    for line in report_lines:
        print(line)

    if args.report:
        print(f"\nReport file written: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
