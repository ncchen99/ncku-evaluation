# 🐍抓抓資料ㄉ小爬🐛
### 需求
```pip install -r requirements.txt```
### 用法
```python3 ./collection/ncku_hub.py```

```python3 ./collection/urschool.py```
### 小屋歸🐢
### 資料來源狀態（2026-11）
- `ncku_hub.py`：從 nckuhub.com 的 API 抓當學期所有課程，每次重建 `data/nckuhub*`，已下架的課程會被移除；失敗太多就不覆蓋舊資料。
- `urschool.py`：urschool.org 已在 2026 年初停止服務，腳本偵測到網站不在就直接結束，保留 `data/urschool*` 裡 2025-06 的最後一份資料。
- 每門課另外記錄評分人數和收穫／涼度／甜度的標準差（`stats` 欄位），擴充功能滑鼠移到評分上會顯示。
- `master` 分支的 GitHub Action（`.github/workflows/update-data.yml`）每月 1 日自動跑爬蟲並推到 `data` 分支，也可以在 Actions 頁面手動執行。
