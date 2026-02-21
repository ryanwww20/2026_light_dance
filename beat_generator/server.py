#!/usr/bin/env python3
"""
後端：提供 .wav 列表、音檔串流、beat_timestamps.csv 讀寫。
CSV 格式：直行 = scene（第 0 欄 = 1-1，第 1 欄 = 1-2），橫列 = beat index；[beat_row, scene_col] = 時間（小數三位）。
執行時請在專案根目錄：python beat_generator/server.py（.wav 取自 beat_generator/ 目錄）
"""

import csv
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

THIS_DIR = Path(__file__).resolve().parent
WAV_DIR = THIS_DIR
BEATS_CSV = THIS_DIR / "beat_timestamps.csv"
SCENE_LIST_FILE = THIS_DIR / "scene_list.txt"

app = Flask(__name__, static_folder=str(THIS_DIR / "static"), static_url_path="")


def _get_scene_list():
    """回傳 scene 表（scene_list.txt 每行一個），順序即 CSV 欄位順序。"""
    if not SCENE_LIST_FILE.exists():
        return []
    lines = SCENE_LIST_FILE.read_text(encoding="utf-8").strip().splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def _list_wav():
    out = []
    for p in WAV_DIR.iterdir():
        if p.suffix.lower() == ".wav":
            out.append(p.name)
    return sorted(out)


def _read_beats_csv():
    """
    CSV 格式：直行 = scene，橫列 = beat index。回傳 { headers: scene 名, rows: 每列 = 同一 beat 各 scene 的時間 }。
    """
    scene_list, scene_rows = _read_scene_rows()
    if not scene_list:
        return {"headers": [], "rows": []}
    max_beats = max(len(sr) for sr in scene_rows) if scene_rows else 0
    rows = [
        [scene_rows[j][i] if i < len(scene_rows[j]) else "" for j in range(len(scene_list))]
        for i in range(max_beats)
    ]
    return {"headers": scene_list, "rows": rows}


def _read_scene_rows():
    """讀取 CSV，回傳 (scene_list, scene_rows)。scene_rows[i] = scene i 的 [t0, t1, ...]（直行 i = scene i）。"""
    scene_list = _get_scene_list()
    if not scene_list:
        return [], []
    scene_rows = [[] for _ in range(len(scene_list))]
    if not BEATS_CSV.exists():
        return scene_list, scene_rows
    with open(BEATS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return scene_list, scene_rows
    header = list(rows[0])
    if len(header) > 0 and (header[0] or "").strip() in scene_list:
        for j, name in enumerate(header):
            name = (name or "").strip()
            if name not in scene_list:
                continue
            scene_idx = scene_list.index(name)
            for r in rows[1:]:
                row = list(r)
                while len(row) <= j:
                    row.append("")
                cell = (row[j] or "").strip()
                scene_rows[scene_idx].append(cell)
        return scene_list, scene_rows
    if len(header) > 0 and (header[0] or "").strip().lower() == "scene":
        for r in rows[1:]:
            row = list(r)
            while len(row) < len(header):
                row.append("")
            scene_name = (row[0] or "").strip()
            if scene_name not in scene_list:
                continue
            scene_idx = scene_list.index(scene_name)
            scene_rows[scene_idx] = [(row[j] or "").strip() for j in range(1, len(header))]
        return scene_list, scene_rows
    return scene_list, scene_rows


def _write_beats_csv(scene_list, scene_rows):
    """直行 = scene，橫列 = beat index。"""
    if not scene_list:
        return
    max_beats = max(len(sr) for sr in scene_rows) if scene_rows else 0
    with open(BEATS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(scene_list)
        for i in range(max_beats):
            row = [scene_rows[j][i] if i < len(scene_rows[j]) else "" for j in range(len(scene_list))]
            writer.writerow(row)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/scenes")
def api_scenes():
    return jsonify(_get_scene_list())


@app.route("/api/wav-files")
def api_wav_files():
    return jsonify(_list_wav())


@app.route("/api/audio/<path:filename>")
def api_audio(filename):
    p = (WAV_DIR / filename).resolve()
    if not str(p).startswith(str(WAV_DIR)) or p.suffix.lower() != ".wav":
        return "", 404
    if not p.exists():
        return "", 404
    return send_from_directory(p.parent, p.name, mimetype="audio/wav")


@app.route("/api/beats", methods=["GET"])
def api_beats_get():
    return jsonify(_read_beats_csv())


@app.route("/api/beats", methods=["POST"])
def api_beats_post():
    data = request.get_json()
    if not data or "scene" not in data or "time" not in data:
        return jsonify({"ok": False, "error": "需要 scene 與 time"}), 400
    try:
        t = float(data["time"])
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "time 須為數字"}), 400
    scene = str(data["scene"]).strip()
    if not scene:
        return jsonify({"ok": False, "error": "scene 不可為空"}), 400
    time_str = f"{t:.3f}"

    scene_list = _get_scene_list()
    if scene not in scene_list:
        return jsonify({"ok": False, "error": f"scene 不在 scene_list.txt 中：{scene}"}), 400

    scene_idx = scene_list.index(scene)
    scene_list, scene_rows = _read_scene_rows()
    beat_idx = len(scene_rows[scene_idx])
    scene_rows[scene_idx].append(time_str)
    _write_beats_csv(scene_list, scene_rows)
    return jsonify({"ok": True, "scene": scene, "time": time_str, "beat_row": beat_idx, "scene_col": scene_idx})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
