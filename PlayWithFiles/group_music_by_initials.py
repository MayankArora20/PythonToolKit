import math
import re
import shutil
from collections import defaultdict
from pathlib import Path


# You can change this if you want a different "safe" size for each folder.
MAX_GROUP_SIZE = 20
MERGE_TARGET_MIN = 15
MERGE_TARGET_MAX = 20


def first_letter(name: str) -> str:
    name = name.strip()
    match = re.match(r"^[^A-Za-z]*([A-Za-z])", name)
    if match:
        return match.group(1).lower()
    return "#"


def split_files(files, prefix: str):
    """Return list of (folder_name, file_paths) based on the 15-20 rule."""
    files = sorted(files, key=lambda p: p.name.lower())
    total = len(files)

    if total <= MERGE_TARGET_MIN:
        return [(prefix, files)]

    if total <= MAX_GROUP_SIZE:
        # split the single letter group into 2 folders when it is above ~15,
        # to keep phone scrolling manageable
        mid = (total + 1) // 2
        return [
            (f"{prefix}1", files[:mid]),
            (f"{prefix}2", files[mid:]),
        ]

    # for very large groups, keep them in chunks of ~20 files
    chunks = max(2, math.ceil(total / MAX_GROUP_SIZE))
    chunk_size = math.ceil(total / chunks)
    result = []
    for idx in range(chunks):
        start = idx * chunk_size
        end = start + chunk_size
        part = files[start:end]
        if part:
            result.append((f"{prefix}{idx + 1}", part))
    return result


def organize_folder(folder_path: str):
    root = Path(folder_path).expanduser()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    file_list = [p for p in root.iterdir() if p.is_file()]
    if not file_list:
        print("No files found in the selected folder.")
        return

    grouped = defaultdict(list)
    for file_path in file_list:
        grouped[first_letter(file_path.name)].append(file_path)

    letters = sorted(grouped.keys())
    final_groups = []
    i = 0

    while i < len(letters):
        current_letter = letters[i]
        current_files = grouped[current_letter]

        # Try to merge with the next letter if combined total is roughly 15-20 files
        if i + 1 < len(letters):
            next_letter = letters[i + 1]
            combined_total = len(current_files) + len(grouped[next_letter])
            if MERGE_TARGET_MIN <= combined_total <= MERGE_TARGET_MAX:
                final_groups.append((f"{current_letter}{next_letter}", current_files + grouped[next_letter]))
                i += 2
                continue

        final_groups.extend(split_files(current_files, current_letter))
        i += 1

    created_dirs = []
    for folder_name, files in final_groups:
        dest = root / folder_name
        dest.mkdir(exist_ok=True)
        created_dirs.append(dest)

        for file_path in files:
            destination = dest / file_path.name
            if destination.exists():
                # avoid overwriting same-named files in the target folder
                stem = file_path.stem
                suffix = 1
                while destination.exists():
                    destination = dest / f"{stem}_{suffix}{file_path.suffix}"
                    suffix += 1
            shutil.move(str(file_path), str(destination))

    print("\nGrouping complete.")
    print("Created folders:")
    for d in created_dirs:
        print(f"- {d.name} : {len(list(d.iterdir()))} files")


if __name__ == "__main__":
    user_path = input("Enter the folder path to organize: ").strip().strip('"')
    organize_folder(user_path)
