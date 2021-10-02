# 載入需要的套件
import subprocess
import pandas as pd
from selenium import webdriver
from time import sleep
version = subprocess.check_output(
    ['google-chrome', '--version']).decode("utf-8").split()[2].split(".")[0]
# 取得 chrome 板本
driver = webdriver.Chrome("./collection/chromedriver/chromedriver" + version)
# 開啟瀏覽器視窗(Chrome)
driver.get("https://course.ncku.edu.tw/index.php")

search_path = ["×", "中文", "課程查詢", "通識類課程", "跨域通識課程", "列表"]
# 可能會遇到 popup 所以需要 "×"

for btn_text in search_path:
    for dom in driver.find_elements_by_xpath(
            "//*[text()='" + btn_text + "']"):
        try:
            dom.click()
            sleep(2)
            break
        except:
            print("按", btn_text, "按鈕失敗")

table = driver.find_element_by_tag_name("table")
course_table = pd.read_html(table.get_attribute('outerHTML'))
print(course_table)
