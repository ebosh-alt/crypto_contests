from pythonpancakes import PancakeSwapAPI
import requests
from bs4 import BeautifulSoup as bs

contract = "0xe070cca5cdfb3f2b434fb91eaf67fa2084f324d7"
link = "https://bscscan.com/token/0xe070cca5cdfb3f2b434fb91eaf67fa2084f324d7"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 YaBrowser/21.3.1.185 Yowser/2.5 Safari/537.36'
}
response = requests.get(url=link, headers=HEADERS).text
if "7,721.77434064108183089" in response or "0x2a16733f52b4aa3976c8131d22ff306b7d543dac".upper() in response:
    print(True)
#page = bs(response.text, 'html.parser')
#print(page)
#info = page.select("div.tab-content")
#print(info)
"""ps = PancakeSwapAPI()
apikey = "Z4HRY6P7K58XI7CKVCEFPPB6HF4VWYC5AD"
info = ps.tokens(contract)
print(info)
link = f"https://api.bscscan.com/api?module=account&action=txlist&address={contract}&startblock=0&endblock=99999999" \
       f"&page=1&offset=20&sort=asc&apikey={apikey}"
print(link)
page_info = requests.get(url=link)
info = page_info.json()
with open("file.csv") as f:
    data = f.read()
for i in info["result"]:
    print(i, '\n')"""
