#!/usr/bin/env python3
"""
從 beat_timestamps.csv 刪除指定 scene 的整欄（該 scene 所有 timestamps 移除）。
CSV 格式：直行 = scene（第 0 欄 = 1-1，第 1 欄 = 1-2），橫列 = beat index。
用法：python delete_scene_beats.py <scene> [scene ...]
例：  python delete_scene_beats.py 1-1
      python delete_scene_beats.py 2-1 2-2
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BEATS_CSV = ROOT / "beat_timestamps.csv"
SCENE_LIST_FILE = ROOT / "scene_list.txt"


def _get_scene_list():
    if not SCENE_LIST_FILE.exists():
        return []
    return [ln.strip() for ln in SCENE_LIST_FILE.read_text(encoding="utf-8").strip().splitlines() if ln.strip()]


def main():
    if len(sys.argv) < 2:
        print("用法：python delete_scene_beats.py <scene> [scene ...]")
        print("例：  python delete_scene_beats.py 1-1")
        print("      python delete_scene_beats.py 2-1 2-2")
        sys.exit(1)

    to_remove = [s.strip() for s in sys.argv[1:] if s.strip()]
    if not to_remove:
        print("請至少指定一個 scene 名稱")
        sys.exit(1)

    scene_list = _get_scene_list()
    if not scene_list:
        print("請先建立 scene_list.txt")
        sys.exit(1)

    removed = [s for s in to_remove if s in scene_list]
    if not removed:
        print("指定的 scene 不在 scene_list.txt 中：", to_remove)
        sys.exit(1)

    # 讀取：直行 = scene，橫列 = beat index
    scene_rows = [[] for _ in range(len(scene_list))]
    if BEATS_CSV.exists():
        with open(BEATS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) > 1:
            header = list(rows[0])
            # header = scene 名
            if (header[0] or "").strip().lower() == "scene":
                # 舊格式：列 = scene
                for r in rows[1:]:
                    row = list(r)
                    while len(row) < len(header):
                        row.append("")
                    scene_name = (row[0] or "").strip()
                    if scene_name not in scene_list:
                        continue
                    idx = scene_list.index(scene_name)
                    scene_rows[idx] = [(row[j] or "").strip() for j in range(1, len(header))]
            else:
                # 新格式：直行 = scene
                for j, name in enumerate(header):
                    name = (name or "").strip()
                    if name not in scene_list:
                        continue
                    idx = scene_list.index(name)
                    for r in rows[1:]:
                        row = list(r)
                        while len(row) <= j:
                            row.append("")
                        scene_rows[idx].append((row[j] or "").strip())

    for scene in removed:
        idx = scene_list.index(scene)
        scene_rows[idx] = []

    max_beats = max(len(sr) for sr in scene_rows) if scene_rows else 0
    with open(BEATS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(scene_list)
        for i in range(max_beats):
            row = [scene_rows[j][i] if i < len(scene_rows[j]) else "" for j in range(len(scene_list))]
            writer.writerow(row)

    print("已刪除 scene 的 timestamps：", ", ".join(removed))
    print(f"已寫回 {BEATS_CSV}")


if __name__ == "__main__":
    main()
