import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

root_url = "https://course.ncku.edu.tw/"
headers = {} # "cookie": "01101_sele_course_F74104765=; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-1124106680%7CMCIDTS%7C18879%7CMCMID%7C73523311519005562792651444219234746358%7CMCAID%7CNONE%7CMCOPTOUT-1631077766s%7CNONE%7CvVersion%7C5.2.0; cos_lang=cht; COURSE_WEB=ffffffff8f7cbb6645525d5f4f58455e445a4a423660; NSC_dpvstf.odlv.fev.ux*bdbedeo=ffffffff8f7ce72c45525d5f4f58455e445a4a42cbdb; PHPSESSID=F74104765c47c7fcf7f75560eb243295368738d83"}
r = requests.get("https://course.ncku.edu.tw/index.php", headers = headers, verify = False)

soup = BeautifulSoup(r.text, 'html.parser')
course_search_url = soup.find('a', text="課程查詢").get("href")
r = requests.get(root_url + course_search_url[1:], headers = headers, verify = False)

search_path = ["通識類課程", "跨域通識課程", "列表"]

for btn_text in search_path:
    soup = BeautifulSoup(r.text, 'html.parser')
    next_i = soup.find('button', text=btn_text).get("onclick")[9:-3]
    print(next_i)
    r = requests.get(root_url + course_search_url[1:] + "&i=" + next_i, headers = headers, verify = False)


course_table = pd.read_html(r.text)

print(course_table)