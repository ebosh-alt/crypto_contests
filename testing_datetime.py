import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import FirefoxOptions

def parsing(urls, periodic_time):
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.58 (Edition Yx 05)'
        }
    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86'
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--headless')
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url=url)
    time.sleep(2)
    frame = driver.find_element(by = By.TAG_NAME, value = "div.table-responsive iframe")
    href = frame.get_attribute("src").replace("&p=1", '')
    print(href)
    page = 1
    stop = False
    while not stop:
        driver.get(f"{href}&p={page}")
        driver.implicitly_wait(5)
        time.sleep(2)
        elements = driver.find_elements(by = By.TAG_NAME, value = "div.table-responsive table tbody tr td")
        #if elements[-5]>periodic_time:
        #    stop = True
        for i in elements:
            print(i.text)
        page+=1

if __name__=="__main__":
    url = "https://bscscan.com/token/0xe070cca5cdfb3f2b434fb91eaf67fa2084f324d7"
    parsing(url)