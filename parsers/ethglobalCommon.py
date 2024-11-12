# https://ethglobal.com/showcase

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import time
import psycopg2

baseuUrl="https://ethglobal.com"
url = "https://ethglobal.com/showcase"

# file = open("ethGlobalCommon.csv", "w")
# file.writelines("hackathon, title, description, page, link\n")
# file.close()

pageCount=1
count=0
while True:
    try:
        page = urlopen(url)
    except HTTPError as hp:
        print(f"end")
        break

    html = page.read().decode("utf-8")
    time.sleep(1)
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select('a.block.border-2.border-black.rounded.overflow-hidden.relative')

    for link in links:
        address = baseuUrl+link["href"]
        title = link.select('h2')[0].text
        description = link.select('p')[0].text
        hackathon = link.select('div')[0].text
        print(f"{hackathon} {title}: {address}")
        file = open("ethGlobalCommon.csv", "a")  # append mode
        file.write(f"{address},{pageCount},{hackathon},{title},{description}\n")
        file.close()
        count=count+1

    pageCount=pageCount+1
    url="https://ethglobal.com/showcase/page/"+str(pageCount)
    print(f"{url}")

file = open("ethGlobalCommon.csv", "a")  # append mode
file.write(f"total projects: {count}\n")
file.close()