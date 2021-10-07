import requests
import json
import threading
import re
import os.path
import pandas as pd
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep
from urllib3.exceptions import InsecureRequestWarning

########################################
#                                      #
#                QQ 丸子               #
#                                      #
########################################


class Worker(threading.Thread):
    def __init__(self, page, lock, semaphore, times):
        threading.Thread.__init__(self)
        self.page = page
        self.lock = lock
        self.times = times
        self.url = "https://urschool.org/teacher/"
        self.semaphore = semaphore

    def run(self):
        # 取得旗標
        # 僅允許有限個執行緒同時進的工作
        global all_professors_table
        self.semaphore.acquire()
        while True:
            proxy = free_proxy_table.sample()
            try:
                r = requests.get(url, params={"page": self.page}, headers=headers, proxies={
                    "https" if proxy["Https"].values[0] == "yes" else "http":
                    str(proxy["IP Address"]) + ":" + str(proxy["Port"])}, timeout=5, verify=False)  # verify=True if proxy["Https"].values[0] == "yes" else False
            except:
                print("save failure at page：", self.page)
                continue

            soup = BeautifulSoup(r.text, 'html.parser')
            id_list = list()
            for tr in soup.find("tbody").find_all("tr"):
                id_list.append(tr.get("id"))

            table = pd.read_html(
                str(soup.find_all("table", class_="table")[0]))[0]
            table["urschool_id"] = id_list
            for index, row in table.iterrows():
                file_name = "./data/urschool/" + str(row["姓名"])
                if os.path.isfile(file_name + ".json"):
                    print("Duplicate professor name:", row["姓名"])
                    file_name += "-2"
                prof_data = row.to_json(orient="records", force_ascii=False)
                with open(file_name + ".json", "w+", encoding="utf-8") as f:
                    json.dump(json.loads(prof_data), f,
                              indent=4, ensure_ascii=False)

            self.lock.acquire()
            all_professors_table = pd.concat(
                [all_professors_table, table], ignore_index=True)

            print("finish page：", self.page)
            self.lock.release()
            break        # 釋放旗標
        self.semaphore.release()

    '''r = requests.get(self.url + self.prof["urschool_id"])
        soup = BeautifulSoup(r.text, "html.parser")
        comments = soup.find('div', id=re.compile('^comment-box-'))
        prof_comments = list()
        try:
            for comment in comments.find_all("div"):
                prof_comments.append({"user": comment.find("img").get(
                    "src"), "comment": comment.find("div").get_text()})
        except:
            print("ERROR saving prof detail")
        file_name = "./data/urschool/" + self.prof["姓名"]
        if os.path.isfile(file_name + ".json"):
            print("Duplicate professor name:", self.prof["姓名"])
            file_name += "-2"
        prof_data = self.prof.to_json(orient="records")
        prof_data["comments"] = prof_comments
        print(prof_data)
        with open(file_name + ".json", "w+", encoding="utf-8") as f:
            json.dump(prof_data, f, indent=4, ensure_ascii=False)'''


all_professors_table = pd.DataFrame()
url = "https://urschool.org/ncku/list"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
# 關閉錯誤訊息
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_how_many_page():
    r = requests.get(url, verify=False, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    return int(soup.find_all("ul", class_="pagination")[0].find_all("li")[-2].get_text())


pages = list(range(1, get_how_many_page()+1))
queue = Queue()
[queue.put(i) for i in pages]
free_proxy_table = pd.read_html(requests.get(
    "https://free-proxy-list.net/", headers=headers).text)[0]


lock = threading.Lock()

# 開 threads 加速
workers = []
# 一次最多可以執行幾個
semaphore = threading.Semaphore(20)

while(not queue.empty()):
    workers.append(Worker(queue.get(), lock, semaphore, 1))
    workers[-1].start()

for worker in workers:
    worker.join()

with open("./data/urschool.json", "w+") as f:
    json.dump(json.loads(all_professors_table.to_json(
        orient="records", force_ascii=False)), f, indent=4, ensure_ascii=False)

# for index, row in all_professors_table.iterrows():
#     file_name = "./data/urschool/" + str(row["姓名"])
#     if os.path.isfile(file_name + ".json"):
#         print("Duplicate professor name:", row["姓名"])
#         file_name += "-2"
#     prof_data = row.to_json(orient="records", force_ascii=False)
#     with open(file_name + ".json", "w+", encoding="utf-8") as f:
#         json.dump(json.loads(prof_data), f, indent=4, ensure_ascii=False)


print("Done.")
