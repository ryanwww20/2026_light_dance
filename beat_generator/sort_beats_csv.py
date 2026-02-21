#!/usr/bin/env python3
"""
將 beat_timestamps.csv 每個 scene 的 timestamps：
1. 由大至小排序
2. 從上而下填滿，不留空缺（空儲存格移除後緊湊排列）

CSV 格式：直行 = scene，橫列 = beat index。
用法：python sort_beats_csv.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BEATS_CSV = ROOT / "beat_timestamps.csv"
SCENE_LIST_FILE = ROOT / "scene_list.txt"


def _get_scene_list():
    if not SCENE_LIST_FILE.exists():
        return []
    return [ln.strip() for ln in SCENE_LIST_FILE.read_text(encoding="utf-8").strip().splitlines() if ln.strip()]


def main():
    scene_list = _get_scene_list()
    if not scene_list:
        print("請先建立 scene_list.txt")
        return

    if not BEATS_CSV.exists():
        print(f"找不到 {BEATS_CSV}")
        return

    with open(BEATS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows or len(rows) < 2:
        print("CSV 無資料列，無需整理")
        return

    header = list(rows[0])
    scene_rows = [[] for _ in range(len(scene_list))]

    if (header[0] or "").strip().lower() == "scene":
        # 舊格式：列 = scene，欄 = beat
        for r in rows[1:]:
            row = list(r)
            while len(row) < len(header):
                row.append("")
            scene_name = (row[0] or "").strip()
            if scene_name not in scene_list:
                continue
            idx = scene_list.index(scene_name)
            for j in range(1, len(header)):
                cell = (row[j] or "").strip()
                if cell:
                    try:
                        scene_rows[idx].append(float(cell))
                    except ValueError:
                        pass
    else:
        # 新格式：直行 = scene，橫列 = beat index
        for j, name in enumerate(header):
            name = (name or "").strip()
            if name not in scene_list:
                continue
            idx = scene_list.index(name)
            for r in rows[1:]:
                row = list(r)
                while len(row) <= j:
                    row.append("")
                cell = (row[j] or "").strip()
                if cell:
                    try:
                        scene_rows[idx].append(float(cell))
                    except ValueError:
                        pass

    # 每個 scene：由小至大排序，轉回字串三位小數（從上而下無空缺）
    for idx in range(len(scene_list)):
        scene_rows[idx].sort()
        scene_rows[idx] = [f"{t:.3f}" for t in scene_rows[idx]]

    # 寫回：直行 = scene，橫列 = beat index
    max_beats = max(len(sr) for sr in scene_rows) if scene_rows else 0
    with open(BEATS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(scene_list)
        for i in range(max_beats):
            row = [scene_rows[j][i] if i < len(scene_rows[j]) else "" for j in range(len(scene_list))]
            writer.writerow(row)

    print(f"已整理 {BEATS_CSV}：每個 scene 由小至大排序、從上而下無空缺")


if __name__ == "__main__":
    main()
