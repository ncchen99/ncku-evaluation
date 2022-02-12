import json
import requests
import threading
import os
import hashlib


class Worker(threading.Thread):
    def __init__(self, course, semaphore):
        threading.Thread.__init__(self)
        self.course = course
        self.semaphore = semaphore

    def run(self):
        # 取得旗標
        # 僅允許有限個執行緒同時進的工作
        self.semaphore.acquire()
        course = self.course
        course_id = str(course["id"])
        course_detail = requests.get(all_courses_url + course_id)
        course_dept_SN = course["系號"] + "-" + course["選課序號"]
        with open("./data/nckuhub/" + course_dept_SN + ".json", "w+") as f:
            json.dump(course_detail.json(),
                      f, indent=4, ensure_ascii=False)
        # 釋放旗標
        self.semaphore.release()
        print("saved {}".format(course_dept_SN))


useful_data = ["got", "cold", "sweet", {"courseInfo": ["課程名稱", "老師"]}]
all_courses_data = {}
all_courses_data["courses"] = {}
all_courses_url = "https://nckuhub.com/course/"
all_courses = requests.get(all_courses_url)

with open("./data/nckuhub_courses.json", "w+") as f:
    json.dump(all_courses.json(),
              f, indent=4, ensure_ascii=False)

# 開 threads 加速
workers = []
# 一次最多可以執行幾個
semaphore = threading.Semaphore(50)

for course in all_courses.json()["courses"]:
    workers.append(Worker(course, semaphore))
    workers[-1].start()


for worker in workers:
    worker.join()


# save title
all_courses_data["column names"] = useful_data

# save courses data
for file in [f for f in os.listdir("./data/nckuhub/") if os.path.isfile(os.path.join("./data/nckuhub/", f))]:
    course_data = json.load(open(os.path.join("./data/nckuhub/", file)))
    course_id = os.path.splitext(file)[0]
    all_courses_data["courses"][course_id] = []
    for idx, key in enumerate(useful_data):
        if isinstance(key, str):
            all_courses_data["courses"][course_id].append(course_data[key])
        else:
            key_name = list(key.keys())[0]
            all_courses_data["courses"][course_id].append({})
            for inner_key in key[key_name]:
                all_courses_data["courses"][course_id][idx][inner_key] = course_data[key_name][inner_key]

# generate sha256
with open("./data/nckuhub-sha256.txt", "w+") as f:
    f.write(hashlib.sha256(json.dumps(
        all_courses_data).encode('utf-8')).hexdigest())

# dump to file
with open("./data/nckuhub.json", "w+") as f:
    json.dump(all_courses_data, f, indent=4, ensure_ascii=False)

print("Done.")
