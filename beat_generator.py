#!/usr/bin/env python3
"""
根據各 scene 的 BPM 產生每段音樂的 beat 秒數，輸出為 CSV。
格式：第一列為標題 scene1, scene2, scene3, ...；每一欄為該 scene 的 beat 秒數（由上而下為第 1、2、3… 拍），小數後三位。
"""

import csv
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="依 BPM 產生各 scene 的 beat 秒數 CSV")
    parser.add_argument(
        "config_csv",
        help="設定檔 CSV，欄位：scene, start_sec, end_sec, bpm",
    )
    parser.add_argument(
        "-o", "--output",
        default="beat_timestamps.csv",
        help="輸出 CSV 檔名（預設：beat_timestamps.csv）",
    )
    parser.add_argument(
        "--beats",
        type=int,
        choices=[4, 8],
        default=4,
        help="每小節幾拍：4 或 8（預設：4）",
    )
    return parser.parse_args()


def load_scenes(config_path: Path):
    """讀取 scene 設定（欄位：scene, start_sec, end_sec, bpm），回傳 [(scene_name, start_sec, end_sec, bpm), ...]。scene 可為 1-1, 2-2, 3-4 等格式。"""
    scenes = []
    with open(config_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("設定檔沒有資料列")
    for row in rows:
        name = str(row["scene"]).strip()
        start = float(row["start_sec"])
        end = float(row["end_sec"])
        bpm = float(row["bpm"])
        scenes.append((name, start, end, bpm))
    return scenes


def generate_beats(start_sec: float, end_sec: float, bpm: float, beats_per_bar: int):
    """
    在 [start_sec, end_sec) 內依 BPM 產生 beat 秒數。
    - beats_per_bar=4：每拍間隔 60/bpm 秒
    - beats_per_bar=8：每拍間隔 30/bpm 秒
    """
    if bpm <= 0:
        return []
    if beats_per_bar == 4:
        interval = 60.0 / bpm
    else:  # 8
        interval = 30.0 / bpm
    out = []
    t = start_sec
    while t < end_sec:
        out.append(round(t, 3))
        t += interval
    return out


def main():
    args = parse_args()
    config_path = Path(args.config_csv)
    if not config_path.exists():
        raise FileNotFoundError(f"找不到設定檔：{config_path}")

    scenes = load_scenes(config_path)
    scene_names = [s[0] for s in scenes]

    # 每欄一個 scene：columns_data[scene_idx] = 該 scene 的 beat 秒數列表
    columns_data = []
    for _name, start, end, bpm in scenes:
        beats = generate_beats(start, end, bpm, args.beats)
        columns_data.append(beats)

    max_beats = max(len(c) for c in columns_data)
    n = len(columns_data)
    out_path = Path(args.output)

    # 寫出 CSV：第一列標題為設定檔的 scene 名稱（如 1-1, 2-2, 3-4）；每欄為該 scene 的 beat 秒數
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(scene_names)
        for row_idx in range(max_beats):
            row = []
            for col_idx in range(n):
                if row_idx < len(columns_data[col_idx]):
                    row.append(f"{columns_data[col_idx][row_idx]:.3f}")
                else:
                    row.append("")
            writer.writerow(row)

    print(f"已寫入 {out_path}，共 {n} 個 scene，beat 模式：{args.beats} 拍")
    for name, beats in zip(scene_names, columns_data):
        print(f"  {name}: {len(beats)} 個 beat")


if __name__ == "__main__":
    main()
