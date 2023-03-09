import re
import requests
from bs4 import BeautifulSoup
import os
import json
import csv
import random
from time import sleep
import datetime


HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0',
}

COOKIES = {'Cookie': ' LANG=ua; store-id=26; '}

DATE = datetime.datetime.today().strftime("%Y.%m.%d")
TIME = datetime.datetime.today().strftime("%H:%M:%S")

OUT_FILENAME = input('Введите имя файла : ')
OUT_FILENAME = OUT_FILENAME.strip()
FOLDER_NAME = "data"
OUT_JSON_FILENAME = f'{FOLDER_NAME}/{OUT_FILENAME}_{DATE}_{TIME}.json'
OUT_CSV_FILENAME = f'{FOLDER_NAME}/{OUT_FILENAME}_{DATE}_{TIME}.csv'

URL = input('Введите URL: ')
URL = URL.strip()

COLUMNS = (
    'Бренд',
    'Атикул',
    'Название продукта',
    'НОВАЯ Цена',
    'Старая цена',
    'Акция'
)


def dump_to_json(filename, data, **kwargs):
    """Сохранение результата в json"""
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    if os.path.exists(FOLDER_NAME):
        print("")
    else:
        os.mkdir(FOLDER_NAME)

    with open(filename, 'w') as f:
        json.dump(data, f, **kwargs)


def dump_to_csv(filename, data):
    """Сохранение результата в CSV"""
    if os.path.exists(FOLDER_NAME):
        print("")
    else:
        os.mkdir(FOLDER_NAME)

    with open(OUT_CSV_FILENAME, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(COLUMNS)
        for item in data:
            writer.writerow([
                item['brend'],
                item['art'],
                item['name'],
                item['price_new'],
                item['price_old'],
                item['stock']
            ])


def get_req(url, params=None):
    """Requests"""
    req_session = requests.Session()
    res = req_session.get(url, headers=HEADERS, cookies=COOKIES, params=params)
    if res.status_code == 200:
        return res.text
    else:
        res = None


def get_soup(res):
    """BeatifulSoup"""
    if res is None:
        print('Error requests !!!')
        soup = None
    else:
        soup = BeautifulSoup(res, features='lxml')
        return soup


def get_page_count(soup):
    """Пагинация страниц"""
    pagination = soup.find_all('a', class_='pagination__item')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def crawl_categories(URL):
    """Собирает ссылки на КАТЕГОРИИ"""
    categories_urls = []
    res = get_req(URL)
    soup = get_soup(res)

    categories_yes_no = soup.find('div', class_='shop-categories')
    if categories_yes_no:
        try:
            categories_title = soup.find(
                'h1', class_='shop-categories__title nc')
            categories_title = categories_title.text.strip()
            all_categories_hrefs = soup.find_all(
                'section', class_='shop-category')
            for tag in all_categories_hrefs:
                href = tag.find(
                    'a', class_='shop-category__title link link--big link--inverted nc')
                href = href.get('href')
                url = '{}'.format(href)
                categories_urls.append(url)
#                print(url)
#            sleep(random.randrange(0, 1))
            print(
                f'\nВ категории "{categories_title}" скопировано {len(categories_urls)} URLs адресов.')

            return categories_urls

        except Exception:
            print('Error categories')
    else:
        print('')


def crawl_products(categories_urls):
    """Собирает со страниц ссылки на товары"""
    products_urls = []
# Товар без группы, категории...
    if categories_urls is None:
        categories_urls = URL
        try:
            res = get_req(categories_urls)
        except Exception:
            print('битый URLs')
        soup = get_soup(res)
        pages_count = get_page_count(soup)
        group_cat = soup.find('h1', class_='nc').text.strip()
        print(f'\tВ группе "{group_cat}" - {pages_count}стр.')
        for page_n in range(1, 1 + pages_count):
            res = get_req(categories_urls, params={'PAGEN_1': page_n})
            soup = get_soup(res)
            all_products_hrefs = soup.find_all(
                'div', class_='columns product-Wrap card-wrapper')
            print(
                f'\tСтраница {page_n} из {pages_count}...  - {len(all_products_hrefs)} URLs')
            for product_href in all_products_hrefs:
                price_yes_no = product_href.find('div', class_='card__price')
                price_yes_no = price_yes_no.find(
                    'span', class_='card__price-sum')
                if price_yes_no is None:
                    break   # print('Нет в наличии')
                else:
                    href = product_href.find('div', class_='card__name')
                    href = href.find(
                        'a', class_='link link--big link--inverted link--blue')
                    href = href.get('href')
                    url = '{}'.format(href)
                    products_urls.append(url)
#        sleep(random.randrange(0, 1))
        print(f'\nВсего URLs с товаром - {len(products_urls)}\n')
        return products_urls

    else:
        categories_urls = categories_urls
        pages_count_categories_urls = 1
        for categorie_url in categories_urls:
            try:
                res = get_req(categorie_url)
            except Exception:
                print('битый URLs')
                break
            soup = get_soup(res)
            pages_count = get_page_count(soup)
            group_cat = soup.find('h1', class_='nc').text.strip()
            print(
                f'\nКатегория: URL - {pages_count_categories_urls} из {len(categories_urls)}...')
            pages_count_categories_urls += 1
            print(f'\tВ группе "{group_cat}" - {pages_count}страниц')
            for page_n in range(1, 1 + pages_count):
                res = get_req(categorie_url, params={'PAGEN_1': page_n})
                soup = get_soup(res)
                all_products_hrefs = soup.find_all(
                    'div', class_='columns product-Wrap card-wrapper')
                print(
                    f'\tСтраница {page_n} из {pages_count}...  - {len(all_products_hrefs)} URLs')
                for product_href in all_products_hrefs:
                    price_yes_no = product_href.find(
                        'div', class_='card__price')
                    price_yes_no = price_yes_no.find(
                        'span', class_='card__price-sum')
                    if price_yes_no is None:
                        break   # print('Нет в наличии')
                    else:
                        href = product_href.find('div', class_='card__name')
                        href = href.find(
                            'a', class_='link link--big link--inverted link--blue')
                        href = href.get('href')
                        url = '{}'.format(href)
                        products_urls.append(url)
#            sleep(random.randrange(0, 1))
        print(f'\nВсего URLs с товаром - {len(products_urls)}\n')
        return products_urls


def parse_products(products_urls):
    """Парсинг полей по каждому товару"""
    data = []

    count = 0
    iteration_count = len(products_urls)
    for product_url in products_urls:
        res = get_req(product_url)
        soup = get_soup(res)
        try:
            brend = soup.find('div', class_='p-block__row p-block__row--char')
            brend = brend.find('a', class_='p-char__brand')
            brend = brend['title'].strip()
        except Exception:
            brend = ''

        try:
            art = soup.find('div', class_='p-block__row p-block__row--status')
            art = art.prettify()    # возвращает строку Unicode, а не байтовую строку
            art = " ".join(re.split('["]+', art))   # Удаление символа "
            # Поиск арт.
            art = re.findall(r"articul :  (\d+)", art,
                             flags=re.MULTILINE | re.DOTALL)
            art = int(''.join(art))     # Преобразование list в int
        except Exception:
            art = ''

        try:
            name = soup.find(
                'header', class_='p-block p-block--header p-header')
            name = name.find('h1', class_='p-header__title nc')
            name = name.text.strip()
        except Exception:
            name = ''

        try:
            price_new = soup.find('div', class_='p-price')
            price_new = price_new.find('div', class_='p-price__main')
            price_new = price_new.text.strip()
            price_new = price_new.replace('грн', '').replace('.', ',')
            price_new = price_new.replace('/рул,', '').replace('/пач,', '')
            price_new = price_new.replace('/упак,', '').replace('/к-т', '')
        except Exception:
            price_new = ''

        try:
            price_old = soup.find('div', class_='p-price')
            price_old = price_old.find('span', class_='p-price__old-sum')
            price_old = price_old.text.strip()
            price_old = price_old.replace('грн', '').replace('.', ',')
            price_old = price_old.replace('/рул,', '').replace('/пач,', '')
            price_old = price_old.replace('/упак,', '').replace('/к-т', '')
        except Exception:
            price_old = ''

        try:
            stock = soup.find('div', class_='p-block__sticky')
            stock = stock.find('span', class_='sticker action')
            stock = stock.text.strip()
            stock = stock.replace('Акція ', '').replace('Акція', '')
            stock = stock.replace('Мегахіт ', '').replace('Мегахіт', '')
            stock = stock.replace('Краща ціна', '')
        except Exception:
            stock = ''

        sleep(random.randrange(0, 2))

        count += 1
        iteration_count = iteration_count - 1
        print(
            f"Итерация #{count} завершена, осталось итераций #{iteration_count}")
        if iteration_count == 0:
            print("\nСбор данных завершен !\n")

        data.append({
            'brend': brend,
            'art': art,
            'name': name,
            'price_new': price_new,
            'price_old': price_old,
            'stock': stock
        })
#    sleep(random.randrange(0, 1))
    return data


def main():
    categories_urls = crawl_categories(URL)
    products_urls = crawl_products(categories_urls)
    data = parse_products(products_urls)
    dump_to_json(OUT_JSON_FILENAME, data)
    dump_to_csv(OUT_CSV_FILENAME, data)


if __name__ == '__main__':
    main()
