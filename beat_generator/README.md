# Beat timestamps 相關腳本、打點器與資料

## 腳本

- **beat_generator.py**：依 BPM 與 scene 時間區段產生 beat 秒數 CSV。  
  `python beat_generator.py <config.csv> [-o beat_timestamps.csv] [--beats 4|8|16]`
- **delete_scene_beats.py**：刪除指定 scene 的整欄 timestamps。  
  `python delete_scene_beats.py <scene> [scene ...]`
- **sort_beats_csv.py**：將每個 scene 的 timestamps 由大至小排序、從上而下填滿無空缺。  
  `python sort_beats_csv.py`

## 打點器網頁（server + static）

- **server.py**：Flask 後端，提供 .wav 列表、音檔、beat CSV 讀寫與 scene 列表。
- **static/**：前端（index.html, style.css, app.js），播放音檔、拖曳音軌、選擇 scene、點擊記錄 beat。

**啟動方式（請在專案根目錄執行）：**
```bash
pip install -r requirements.txt   # 根目錄的 requirements.txt
python beat_generator/server.py
```
瀏覽器開啟 http://localhost:5000 。.wav 檔會從專案根目錄讀取。

## 資料檔

- **scene_list.txt**：scene 名稱列表（每行一個），順序對應 CSV 直行。
- **beat_timestamps.csv**：直行 = scene，橫列 = beat index；由打點器或 beat_generator 寫入。

執行腳本時可在專案根目錄執行（例如 `python beat_generator/beat_generator.py ...`）或 `cd beat_generator` 後執行。
