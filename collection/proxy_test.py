from pandas.core.indexes.base import ensure_index_from_sequences
import requests
import json
import threading
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
pages = list(range(1, 280))
free_proxy_table = pd.read_html(requests.get(
    "https://free-proxy-list.net/", headers=headers).text)[0]
url = "https://urschool.org/ncku/list"

proxy = free_proxy_table.sample()
page = 1

if proxy["Https"].values[0] == "yes":
    proxy_detail = {"https": str(
        proxy["IP Address"]) + ":" + str(proxy["Port"])}
else:
    proxy_detail = {"http": str(
        proxy["IP Address"]) + ":" + str(proxy["Port"])}
r = requests.get(url, params={"page": page}, headers=headers,
                 proxies=proxy_detail, verify=True if proxy["Https"].values[0] == "yes" else False)

print(r.text)
