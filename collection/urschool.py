import requests
import json
import threading
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep

########################################
#                                      #
#          可能需要 free proxy          #
#                                      #
########################################

# class Worker(threading.Thread):
#     def __init__(self, course, semaphore):
#         threading.Thread.__init__(self)
#         self.course = course
#         self.semaphore = semaphore

#     def run(self):
#         # 取得旗標
#         # 僅允許有限個執行緒同時進的工作
#         self.semaphore.acquire()

#         course = self.course
#         course_id = str(course["id"])
#         course_detail = requests.get(all_courses_url + course_id)
#         course_dept_SN = course["系號"] + "-" + course["選課序號"]
#         with open("./data/nckuhub/" + course_dept_SN + ".json", "w+") as f:
#             json.dump(course_detail.json(),
#                       f, indent=4, ensure_ascii=False)

#         # 釋放旗標
#         self.semaphore.release()


all_professors_table = pd.DataFrame()


def get_page(page):
    global all_professors_table
    r = requests.get(url, params={"page": page})
    soup = BeautifulSoup(r.text, 'html.parser')
    id_list = list()
    for tr in soup.find("tbody").find_all("tr"):
        id_list.append(tr.get("id"))
    table = pd.read_html(
        str(soup.find_all("table", class_="table")[0]))[0]

    table["urschool_id"] = id_list
    all_professors_table = pd.concat(
        [all_professors_table, table], ignore_index=True)


url = "https://urschool.org/ncku/list"
threads = []
# 暫時想不到比較好的寫法 學校的老師應該不會超過 300 頁
for page in range(1, 300):
    threads.append(threading.Thread(target=get_page, args=(page,)))
    threads[-1].start()
    print("Getting page", page)
    if not(page % 10):
        sleep(50)

for thread in threads:
    thread.join()


with open("./data/urschool.json", "w+") as f:
    json.dump(json.loads(all_professors_table.to_json(
        orient="split", force_ascii=False)), f, indent=4, ensure_ascii=False)

# # 開 threads 加速
# workers = []
# # 一次最多可以執行幾個
# semaphore = threading.Semaphore(50)

# for course in all_courses.json()["courses"]:
#     workers.append(Worker(course, semaphore))
#     workers[-1].start()
#     print("saving {}".format(course["id"]))

# for worker in workers:
#     worker.join()

# print("Done.")
