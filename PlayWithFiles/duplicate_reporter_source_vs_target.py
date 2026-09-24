#!/usr/bin/env python3
"""Compare files from one source folder against a target folder and its subfolders.

Important:
- Folder path is NOT a duplicate criterion.
- Files are compared by filename similarity and content metadata, not by where they live.
- This script only scans the source root for files and scans the target root recursively.
- It also reports whether the source and target folder structures match.

Output format:
    file1Path|file2Path|reason

No deletion is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm"}


def normalize_name(name: str) -> str:
    raw = Path(name).stem.lower()
    raw = re.sub(r"[_\-\.]+", " ", raw)
    raw = re.sub(r"[^a-z0-9 ]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def file_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "other"


def file_name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_percent_diff(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        return 0.0
    return abs(a - b) / max(a, b)


def get_audio_quality(path: Path) -> Dict[str, float]:
    info: Dict[str, float] = {}
    try:
        import mutagen
        from mutagen import File as MutagenFile

        meta = MutagenFile(path, easy=True)
        if meta is not None:
            info_info = getattr(meta, "info", None)
            if info_info is not None:
                bitrate = getattr(info_info, "bitrate", 0) or 0
                sample_rate = getattr(info_info, "sample_rate", 0) or 0
                length = getattr(info_info, "length", 0) or 0
                if bitrate:
                    info["bitrate"] = float(bitrate)
                if sample_rate:
                    info["sample_rate"] = float(sample_rate)
                if length:
                    info["duration"] = float(length)
    except Exception:
        pass

    if info:
        return info

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
            stream = next((s for s in payload.get("streams", []) if s.get("codec_type") == "audio"), {})
            fmt = payload.get("format", {})
            bitrate = stream.get("bit_rate") or fmt.get("bit_rate")
            sample_rate = stream.get("sample_rate")
            duration = fmt.get("duration")
            if bitrate:
                info["bitrate"] = float(bitrate)
            if sample_rate:
                info["sample_rate"] = float(sample_rate)
            if duration:
                info["duration"] = float(duration)
    except Exception:
        pass

    return info


def get_image_quality(path: Path) -> Dict[str, float]:
    try:
        from PIL import Image

        with Image.open(path) as img:
            return {"width": float(img.width), "height": float(img.height)}
    except Exception:
        return {}


def get_media_quality(path: Path) -> Dict[str, float]:
    ext = path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return get_audio_quality(path)
    if ext in IMAGE_EXTENSIONS:
        return get_image_quality(path)
    return {}


def collect_files(folder: str, recursive: bool) -> List[Path]:
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    if recursive:
        iterator = root.rglob("*")
    else:
        iterator = root.iterdir()

    files: List[Path] = []
    for path in iterator:
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.name.lower())


def collect_relative_directories(folder: str, recursive: bool) -> Set[str]:
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    dirs: Set[str] = set()
    if recursive:
        for path in root.rglob("*"):
            if path.is_dir():
                rel = path.relative_to(root).as_posix()
                if rel != ".":
                    dirs.add(rel)
    else:
        for path in root.iterdir():
            if path.is_dir():
                dirs.add(path.name)
    return dirs


def is_likely_duplicate(file1: Path, file2: Path, similarity_threshold: float) -> bool:
    if file_type(file1) != file_type(file2):
        return False

    name_score = file_name_similarity(file1.name, file2.name)
    same_name = file1.name.lower() == file2.name.lower()
    if same_name:
        return True
    if name_score >= similarity_threshold:
        return True
    return False


def build_reason(file1: Path, file2: Path) -> str:
    score = file_name_similarity(file1.name, file2.name)
    reasons = [f"name_score={score:.2f}"]

    if file1.name.lower() == file2.name.lower():
        reasons.append("same_name=True")

    reason_type = file_type(file1)
    reasons.append(f"type={reason_type}")

    size1 = file1.stat().st_size
    size2 = file2.stat().st_size
    diff = safe_percent_diff(size1, size2)
    reasons.append(f"size_diff={diff:.2%}")

    if size1 == size2:
        reasons.append("same_size=True")

    if file1.suffix.lower() == file2.suffix.lower():
        reasons.append("same_extension=True")

    try:
        if sha256_file(file1) == sha256_file(file2):
            reasons.append("same_hash=True")
    except Exception:
        pass

    q1 = get_media_quality(file1)
    q2 = get_media_quality(file2)
    if reason_type == "audio":
        br1 = q1.get("bitrate")
        br2 = q2.get("bitrate")
        sr1 = q1.get("sample_rate")
        sr2 = q2.get("sample_rate")
        if br1 and br2:
            reasons.append(f"bitrate={int(br1)} vs {int(br2)}")
        if sr1 and sr2:
            reasons.append(f"sample_rate={int(sr1)} vs {int(sr2)}")
    elif reason_type == "image":
        w1 = q1.get("width")
        w2 = q2.get("width")
        h1 = q1.get("height")
        h2 = q2.get("height")
        if w1 and w2 and h1 and h2:
            reasons.append(f"resolution={int(w1)}x{int(h1)} vs {int(w2)}x{int(h2)}")

    return "; ".join(reasons)


def compare_source_to_target(source_folder: str, target_folder: str, similarity_threshold: float = 0.75) -> Tuple[List[str], List[str]]:
    source_files = collect_files(source_folder, recursive=False)
    target_files = collect_files(target_folder, recursive=True)

    source_dirs = collect_relative_directories(source_folder, recursive=False)
    target_dirs = collect_relative_directories(target_folder, recursive=True)

    report_lines: List[str] = []
    for src in source_files:
        for tgt in target_files:
            if not is_likely_duplicate(src, tgt, similarity_threshold):
                continue
            report_lines.append(f"{src}|{tgt}|{build_reason(src, tgt)}")

    structure_lines: List[str] = []
    missing_in_source = sorted(target_dirs - source_dirs)
    missing_in_target = sorted(source_dirs - target_dirs)
    for folder in missing_in_source:
        structure_lines.append(f"STRUCTURE|{folder}|source_missing|target_present|folder_present_only_in_target")
    for folder in missing_in_target:
        structure_lines.append(f"STRUCTURE|{folder}|source_present|target_missing|folder_present_only_in_source")

    if not missing_in_source and not missing_in_target:
        structure_lines.append("STRUCTURE|MATCH|same_structure|same_structure|folder_structure_is_aligned")

    return sorted(set(report_lines)), structure_lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare source folder files to target folder and target subfolders.")
    parser.add_argument("source_folder", help="Source folder to compare")
    parser.add_argument("target_folder", help="Target folder to compare against")
    parser.add_argument("--report", help="Optional output file for the duplicate report")
    parser.add_argument("--threshold", type=float, default=0.75, help="Name similarity threshold (0.0-1.0). Default: 0.75")
    args = parser.parse_args()

    try:
        report_lines, structure_lines = compare_source_to_target(args.source_folder, args.target_folder, args.threshold)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_lines = report_lines + structure_lines
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(output_lines) + ("\n" if output_lines else ""), encoding="utf-8")

    if not output_lines:
        print("No likely duplicates or folder structure differences found.")
        if args.report:
            print(f"Report written: {args.report}")
        return 0

    for line in output_lines:
        print(line)

    if args.report:
        print(f"\nReport written: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
