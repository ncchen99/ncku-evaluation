from pandas.core.indexes.base import ensure_index_from_sequences
import requests
import json
import threading
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from urllib3.exceptions import InsecureRequestWarning


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
url = "https://urschool.org/ncku/list"
threads = []
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
pages = list(range(1, 210))
free_proxy_table = pd.read_html(requests.get(
    "https://free-proxy-list.net/", headers=headers).text)[0]
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_page(page):
    global all_professors_table
    global pages
    proxy = free_proxy_table.sample()
    try:
        r = requests.get(url, params={"page": page}, headers=headers, proxies={
            "https" if proxy["Https"].values[0] == "yes" else "http":
            str(proxy["IP Address"]) + ":" + str(proxy["Port"])}, timeout=5, verify=False)  # verify=True if proxy["Https"].values[0] == "yes" else False
    except:
        pages.append(page)
        print("save failure at page：", page)
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    id_list = list()
    for tr in soup.find("tbody").find_all("tr"):
        id_list.append(tr.get("id"))
    table = pd.read_html(
        str(soup.find_all("table", class_="table")[0]))[0]

    table["urschool_id"] = id_list
    all_professors_table = pd.concat(
        [all_professors_table, table], ignore_index=True)
    print("finish page：", page)


# 暫時想不到比較好的寫法 學校的老師應該不會超過 210 頁
while(pages):
    page = pages.pop()
    threads.append(threading.Thread(target=get_page, args=(page,)))
    threads[-1].start()
    if not(page % 15):
        print(len(pages), "pages left")
        sleep(10)

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
