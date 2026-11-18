"""Scrape course ratings from NCKU Hub (https://nckuhub.com).

Output:
  data/nckuhub_courses.json   raw course list of the current semester
  data/nckuhub/<系號>-<選課序號>.json   raw detail of each course
  data/nckuhub.json           compact data consumed by the Chrome extension
  data/nckuhub-sha256.txt     hash of nckuhub.json, used by the extension's cache

The data is rebuilt from scratch on every run, so courses that are no longer
offered are removed. If anything goes badly wrong, nothing is overwritten.
"""
import hashlib
import json
import os
import shutil
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "https://nckuhub.com/course/"
DATA_DIR = "./data"
DETAIL_DIR = os.path.join(DATA_DIR, "nckuhub")
TMP_DIR = DETAIL_DIR + ".tmp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
}
WORKERS = 4
RETRIES = 4
# Abort (keep old data) if more than this ratio of courses fail.
MAX_FAILURE_RATIO = 0.02

useful_data = ["got", "cold", "sweet", {"courseInfo": ["課程名稱", "老師"]}]
# 額外計算的欄位（放在最後，舊版擴充功能只讀前 4 個欄位）
STAT_KEYS = ["got", "cold", "sweet"]
column_names = useful_data + [{"stats": ["人數", "標準差"]}]

session = requests.Session()
session.headers.update(HEADERS)


def get_json(url):
    for attempt in range(RETRIES):
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            if attempt == RETRIES - 1:
                raise
            print(f"retry {url}: {e}")
            time.sleep(2 ** attempt)


def fetch_course(course):
    key = f'{course["系號"]}-{course["選課序號"]}'
    detail = get_json(BASE_URL + str(course["id"]))
    if "courseInfo" not in detail:
        raise ValueError(f"unexpected response for {key}")
    with open(os.path.join(TMP_DIR, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(detail, f, indent=4, ensure_ascii=False)
    return key, detail


def rating_stats(detail):
    """評分人數，以及收穫／涼度／甜度各自的樣本標準差（人數 < 2 時為 None）。"""
    rates = detail.get("rates") or []
    count = detail.get("rate_count") or len(rates)
    sd = []
    for k in STAT_KEYS:
        values = [r[k] for r in rates if isinstance(r.get(k), (int, float))]
        sd.append(round(statistics.stdev(values), 2) if len(values) >= 2 else None)
    return {"人數": count, "標準差": sd}


def compact(detail):
    row = []
    for key in useful_data:
        if isinstance(key, str):
            row.append(detail[key])
        else:
            name = list(key.keys())[0]
            row.append({k: detail[name][k] for k in key[name]})
    row.append(rating_stats(detail))
    return row


def main():
    course_list = get_json(BASE_URL)
    courses = course_list.get("courses") or []
    if not courses:
        sys.exit("NCKU Hub returned an empty course list, keep old data.")
    print(f"{len(courses)} courses in the list")

    shutil.rmtree(TMP_DIR, ignore_errors=True)
    os.makedirs(TMP_DIR)

    results, failures = {}, []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(fetch_course, c): c for c in courses}
        for i, future in enumerate(as_completed(futures), 1):
            course = futures[future]
            try:
                key, detail = future.result()
                results[key] = compact(detail)
            except Exception as e:  # noqa: BLE001
                failures.append(course["id"])
                print(f"Failed to save {course['id']}: {e}")
            if i % 200 == 0:
                print(f"{i}/{len(courses)}")

    if len(failures) > len(courses) * MAX_FAILURE_RATIO:
        shutil.rmtree(TMP_DIR, ignore_errors=True)
        sys.exit(f"{len(failures)} courses failed, keep old data.")

    all_courses_data = {
        "courses": dict(sorted(results.items())),
        "column names": column_names,
    }

    shutil.rmtree(DETAIL_DIR, ignore_errors=True)
    os.rename(TMP_DIR, DETAIL_DIR)
    with open(os.path.join(DATA_DIR, "nckuhub_courses.json"), "w", encoding="utf-8") as f:
        json.dump(course_list, f, indent=4, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "nckuhub-sha256.txt"), "w") as f:
        f.write(hashlib.sha256(json.dumps(all_courses_data).encode("utf-8")).hexdigest())
    with open(os.path.join(DATA_DIR, "nckuhub.json"), "w", encoding="utf-8") as f:
        json.dump(all_courses_data, f, indent=4, ensure_ascii=False)

    print(f"Done. {len(results)} courses saved, {len(failures)} failed.")


if __name__ == "__main__":
    main()
