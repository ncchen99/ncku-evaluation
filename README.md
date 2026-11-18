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
