#!/usr/bin/env python3
"""Find duplicate files by exact file name across two folders.

What it does:
- accepts two folder paths
- scans both folders recursively
- groups files by exact file name (case-insensitive)
- compares their size and extension
- optionally analyzes actual content with SHA-256
- shows the "better" candidate based on a simple quality score
- asks before deleting duplicates

This version intentionally focuses on exact file names only, as requested.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm"}


def normalize_name(name: str) -> str:
    return name.lower()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_readable_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024 or unit == "TB":
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def quality_score(path: Path) -> float:
    """Simple quality heuristic.

    For music, use bitrate if available; for images use dimensions if available.
    Otherwise fall back to file size.
    """
    size = path.stat().st_size
    ext = path.suffix.lower()

    score = float(size)

    try:
        if ext in AUDIO_EXTENSIONS:
            # Try to read metadata with standard library for a few audio formats.
            # For .mp3/.wav it is often not available, so we fall back to size.
            import wave

            if ext == ".wav":
                with wave.open(str(path), "rb") as wf:
                    score += float(wf.getframerate() * wf.getnchannels() * wf.getsampwidth())
            elif ext == ".mp3":
                # No standard mp3 metadata parser here; keep size-based score.
                pass
    except Exception:
        pass

    try:
        if ext in IMAGE_EXTENSIONS:
            from PIL import Image

            with Image.open(path) as img:
                score += float(img.width * img.height)
    except Exception:
        pass

    return score


def scan_folder(folder: str) -> Dict[str, List[Path]]:
    results: Dict[str, List[Path]] = {}
    root = Path(folder)

    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    for file_path in root.rglob("*"):
        if file_path.is_file():
            results.setdefault(normalize_name(file_path.name), []).append(file_path)
    return results


def find_duplicate_groups(folder_a: str, folder_b: str) -> List[dict]:
    files_a = scan_folder(folder_a)
    files_b = scan_folder(folder_b)

    matches = sorted(set(files_a) & set(files_b))
    groups = []

    for name in matches:
        candidates = files_a.get(name, []) + files_b.get(name, [])
        if len(candidates) < 2:
            continue

        unique_candidates = []
        seen = set()
        for candidate in candidates:
            resolved = str(candidate.resolve())
            if resolved not in seen:
                unique_candidates.append(candidate)
                seen.add(resolved)

        groups.append({
            "file_name": name,
            "candidates": unique_candidates,
        })

    return groups


def print_group_summary(group: dict) -> None:
    name = group["file_name"]
    print(f"\n=== Duplicate file name: {name} ===")
    for idx, file_path in enumerate(group["candidates"], start=1):
        size = file_path.stat().st_size
        print(f"  [{idx}] {file_path} | {safe_readable_size(size)} | ext={file_path.suffix.lower()}")


def confirm(prompt: str) -> bool:
    answer = input(prompt).strip().lower()
    return answer in {"y", "yes"}


def analyze_content(group: dict) -> Tuple[bool, Dict[str, List[Path]]]:
    hashes: Dict[str, List[Path]] = {}
    for path in group["candidates"]:
        digest = sha256_file(path)
        hashes.setdefault(digest, []).append(path)

    identical_groups = [paths for paths in hashes.values() if len(paths) > 1]
    return (len(identical_groups) > 0), hashes


def decide_keep_path(group: dict) -> Path:
    """Choose the best candidate using a simple score. Higher is better."""
    ranked = sorted(group["candidates"], key=lambda p: quality_score(p), reverse=True)
    return ranked[0]


def delete_duplicates(group: dict, keep_path: Path) -> None:
    deleted = 0
    for file_path in group["candidates"]:
        if file_path == keep_path:
            continue
        try:
            file_path.unlink()
            print(f"Deleted: {file_path}")
            deleted += 1
        except Exception as exc:
            print(f"Could not delete {file_path}: {exc}")
    print(f"Removed {deleted} duplicate file(s) for {group['file_name']}.")


def main() -> int:
    if len(sys.argv) >= 3:
        folder_a = sys.argv[1]
        folder_b = sys.argv[2]
    else:
        print("Enter the two folders to compare.")
        folder_a = input("Folder 1: ").strip()
        folder_b = input("Folder 2: ").strip()

    if not folder_a or not folder_b:
        print("Both folder paths are required.")
        return 1

    try:
        duplicate_groups = find_duplicate_groups(folder_a, folder_b)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1

    if not duplicate_groups:
        print("No exact-name duplicates found between the two folders.")
        return 0

    print(f"\nFound {len(duplicate_groups)} duplicate name group(s).")

    for group in duplicate_groups:
        print_group_summary(group)

        keep_path = decide_keep_path(group)
        print(f"Preferred file to keep: {keep_path} (best score by size/quality heuristic)")

        if confirm("\nAnalyze actual content to confirm duplicates? [Y/N]: "):
            has_identical_contents, hashes = analyze_content(group)
            if has_identical_contents:
                print("Some files are exact byte-for-byte duplicates.")
                for digest, paths in hashes.items():
                    if len(paths) > 1:
                        print(f"  Hash {digest[:12]}: {', '.join(str(p) for p in paths)}")
            else:
                print("Same file names were found, but their contents are different. They are not exact duplicates.")

        if confirm("\nDelete duplicate(s) and keep the better file? [Y/N]: "):
            delete_duplicates(group, keep_path)
        else:
            print("Skipped deletion for this group.")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
