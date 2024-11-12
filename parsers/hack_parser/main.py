import psycopg2

import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import time
import psycopg2
from settings import \
    SAVE_DIR, \
    PSQL_HOST, \
    PSQL_PORT, \
    PSQL_USER, \
    PSQL_PASSWORD, \
    PSQL_NAME

baseuUrl="https://ethglobal.com"
url = "https://ethglobal.com/showcase"

# file = open("ethGlobalCommon.csv", "w")
# file.writelines("hackathon, title, description, page, link\n")
# file.close()

print("Get submissions from ", baseuUrl)
conn = psycopg2.connect(database=PSQL_NAME,
                        host=PSQL_HOST,
                        user=PSQL_USER,
                        password=PSQL_PASSWORD,
                        port=PSQL_PORT)
cursor = conn.cursor()

pageCount=1
count=0
while True:
    print("loading page")
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        print("page loaded")
        soup = BeautifulSoup(response, "html.parser")
        links = soup.select('a.block.border-2.border-black.rounded.overflow-hidden.relative')

        print("parsing links")
        for link in links:
            print(f"{link}")
            address = baseuUrl+link["href"]
            title = link.select('h2')[0].text
            description = link.select('p')[0].text
            hackathon = link.select('div')[0].text
            print(f"{hackathon} {title}: {address}")
            # file = open("ethGlobalCommon.csv", "a")  # append mode
            # file.write(f"{address},{pageCount},{hackathon},{title},{description}\n")
            # file.close()
            count=count+1

        pageCount=pageCount+1
        url="https://ethglobal.com/showcase/page/"+str(pageCount)
        print(f"parsed {url}")

    else:
        print(f"Ошибка при загрузке страницы: {response.status_code}")