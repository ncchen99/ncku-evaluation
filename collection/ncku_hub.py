import json
import requests
import threading


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
    print("saving {}".format(course["id"]))

for worker in workers:
    worker.join()

print("Done.")
