import asyncio
import aiohttp
import aiofiles
import os
import re

from bs4 import BeautifulSoup as BS
from random import uniform
from time import monotonic as mt

BASE_URL = 'https://bash.im{}'
CALENDAR_URL = BASE_URL.format('/comics-calendar/{}')


async def fetch_imgs(url, session, sleep_range):
    """Получение и сохранение картинок комиксов

    url - адрес картинки
    session - объект aiohttp.ClientSession
    sleep_range - кортеж, диапазон задержки запуска корутины
    """
    await asyncio.sleep(uniform(*sleep_range))
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                dirname = 'images'
                if os.path.exists(dirname) and os.path.isdir:
                    filename = os.path.join(dirname, url.rpartition('/')[-1])
                else:
                    os.mkdir(dirname)
                    filename = os.path.join(dirname, url.rpartition('/')[-1])
                try:
                    async with aiofiles.open(filename, 'wb') as f:
                        await f.write(data)
                        print(f'Файл {filename} сохранен.')
                except IOError:
                    print(f'Не могу записать файл: {filename}')
            else:
                print(
                    f'Ошибка загрузки изображения {url}. Ответ сервера: {response.status}')
    except aiohttp.client_exceptions.ClientConnectorError:
        print(f'Сбой подключения к серверу при обращении по адресу: {url}')
        # Попытка обработки сбоя подключения и повторный запрос к серверу
        print(f'Пытаемся загрузить данные с адреса {url} снова')
        sleep_range = (5, 10)
        async with aiohttp.ClientSession(trust_env=True) as session:
            task = asyncio.create_task(fetch_imgs(url, session, sleep_range))
            data = await asyncio.gather(task)


async def fetch_html(url, session, sleep_range):
    """Получение списка ссылок на странички картинок комиксов
    и сами картинки

    url - адрес картинки
    session - объект aiohttp.ClientSession
    sleep_range - кортеж, диапазон задержки запуска корутины
    """
    await asyncio.sleep(uniform(*sleep_range))
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.text()
                data = BS(data, "html.parser")
                # return data
            else:
                print(
                    f'Ошибка при заросе {url}. Response status: {response.status}')
                data = None
    except aiohttp.client_exceptions.ClientConnectorError:
        print(f'Сбой подключения к серверу при обращении по адресу: {url}')
        # Попытка обработки сбоя подключения и повторный запрос к серверу
        print(f'Пытаемся загрузить данные с адреса {url} снова')
        sleep_range = (1, 5)
        async with aiohttp.ClientSession(trust_env=True) as session:
            task = asyncio.create_task(fetch_html(url, session, sleep_range))
            data = await asyncio.gather(task)
        data = data[0]
    finally:
        return data


async def main(year):
    # Получение списка ссылок на странички комиксов
    url = CALENDAR_URL.format(year)
    sleep_range = (1, 2)
    async with aiohttp.ClientSession(trust_env=True) as session:
        task = asyncio.create_task(fetch_html(url, session, sleep_range))
        data = await asyncio.gather(task)

    soup = data[0]
    if soup:
        div = soup.find(id="calendar")
        if div:
            data = []
            code = r'^<a href="(.*)"><.*'
            regexp = re.compile(code)
            for elem in div.find_all('a'):
                data.append(regexp.match(str(elem)).group(1))
            print(data[:10])

        urls = [BASE_URL.format(elem) for elem in data[:10]]
        print(urls)

    # Установим диапазон случайной задержки для избежания шторма запросов на сервер
        sleep_range = (2, 5)
    # Получение списка ссылок на картинки комиксов
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [asyncio.create_task(fetch_html(url, session, sleep_range))
                     for url in urls]
            data = await asyncio.gather(*tasks)

        imgs = []
        for soup in data:
            if soup:
                img = soup.find(id="cm_strip")
                if img:
                    code = r'^<img.*src="(.*)".*>'
                    regexp = re.compile(code)
                    data = regexp.match(str(img)).group(1)
                    imgs.append(data)
        print(imgs)

    # Получение и сохранение картинок комиксов
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [asyncio.create_task(fetch_imgs(url, session, sleep_range))
                     for url in imgs if url]
            data = await asyncio.gather(*tasks)


print('Asynchronous requests')
t = mt()
year = 2017
asyncio.run(main(year))
print('Finishing in {} sec.'.format(mt() - t))
