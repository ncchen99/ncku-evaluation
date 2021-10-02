# 載入需要的套件
from selenium import webdriver

driver = webdriver.Chrome("./crawler/chromedriver")
str1 = driver.capabilities['browserVersion']
print(str1)
# 開啟瀏覽器視窗(Chrome)
# 方法一：執行前需開啟chromedriver.exe且與執行檔在同一個工作目錄
# driver = webdriver.Chrome()
# 方法二：或是直接指定exe檔案路徑
