import asyncio
import aiohttp
import aiofiles
import json
import re
import requests

from bs4 import BeautifulSoup as BS
from time import monotonic as mt

"""
1. Получить список ссылок на странички комиксов
2. Получить ссылку на картинку комиксов
3. Скачать картинки по ссылкам
"""

code= r'^<a href="(.*)"><.*'
regexp = re.compile(code)

URL_BASE = 'http://bash.im'
URL = ''.join([URL_BASE, '/comics-calendar/{}'])
proxies = {
    'http': 'http://localhost:3128',
    'https': 'http://localhost:3128',
}

proxy = 'http://localhost:3128'

async def fetch_album(year, session):
    global URL
    url = URL.format(year)
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            # response.text() - текст
            # response.content() - файлы - картинки например
            return data
        print(f'Error fetching index {year}')
        return None

async def fetch_html(year, session):
    global URL
    url = URL.format(year)
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.text()
            # response.text() - текст
            # response.content() - файлы - картинки например
            soup = BS(data, "html.parser")
            div = soup.find(id="calendar")
            if div:
                data = []
                for elem in div.find_all('a'):
                    data.append(regexp.match(str(elem)).group(1))
            return data
        print(f'Error fetching {url}. Response status: {response.status}')
        return None

async def main(year):
    # Получить список ссылок
    async with aiohttp.ClientSession(trust_env=True) as session:
        task = asyncio.create_task(fetch_html(year, session))
        data = await asyncio.gather(task)
    print(data)
    # filename = 'D:\\EDU\\PYTHON\\homework\\bashim_comics\\bash.im_comics-calendar_2018.html'
    # async with aiofiles.open(filename, 'r', encoding='windows-1251') as f:
    #     data = await f.read()
    # print(data)
    # print(div.find_all('a'))

            
#     <div id = "calendar" >
# <a href = "/comics/20180101" > <img src = "https://bash.im/img/ts/uv2b5ewuuqllndzi448160.png" width = "40" height = "40" > </a >
# </div >


#     # Скачать файлы
#     async with aiohttp.ClientSession() as session:
#         tasks = [asyncio.create_task(fetch_album(i, session))
#                  for i in range(1, 101)]
#         data = await asyncio.gather(*tasks)
#         # for d in data:
#         #     if d:
#         #         print(d['title'])

print('Asynchronous requests')
t = mt()
year = 2017
asyncio.run(main(year))
print('Finishing in {} sec.'.format(mt()-t))
