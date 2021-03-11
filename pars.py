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
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
        }

COOKIES = {'Cookie': '__cfduid=d036f903509c1f6e668b7a46bb968586d1614844774; PHPSESSID=v92vkjkps7s6vb8042f7caegpb; LANG=ua; store-id=26; BITRIX_SM_LOCATION=def50200cb706377796132e6cf8f7d15af1d9dda1651dc9d2177eee42ce10af3f4e6aa3528e998fe92ff21273d385e216bd4a9b861f405231369db6b091b2381d6578d7c0b2fcf36ffe60eff36a51278884fcfb15a7bf6645c58394a48df31a0976fcc11cef1638673a3800b3f4e0f637aafea46ab2170dfbcde5a43420685122eb3cecba672e7dcdbcb85920ee3147b08c5c84965900c3eb4dc75869ee263162e0c263f656535eb460fde3dfc472e91c5e51bbd3b0a206b8c4a21dea3c9e4d02927fc1a1355cd2312eedd54d3a03875cc68562956be7ac1c54827c7256de58fafd519ae3901753b49abdf712582cfef00411da95d590b94aeab03c85b16500f0510974a05042d15b91320ecb99caf364f257d3f92ea7fcbce0cc2ec417e01bcd1e8a22c91670bc56e1b09cd0c7e84a05a3796f31da4fb308971c027177147a97a9c5fca6b637ce9fc2d7a8a867486b7a159895f816f6ef9916af3d0810223fccb84a901422e9550097441f2199d2c1a5146fbb62bf225ee007f2761b2044e5279ceff77a72f6ffc3f55be46228bfbdb68f5bc0fe696c35029605f486de0453429917905bb58f0ad1046b77d0d9875664589f80febc0f2475b68fbd3b734fe6160988ed08d4e9cdf369b852fa3113316f24b7984f61eae517f9a69fd219d7b36333d3bf61ccab49b8fd696f5d748ffc81f49e5566d7f42e52f5d48cc2b3ad2349b4caa84371adc21bfbbb2c672bc3b6de73efb78053a008fdec375fdca6953f803bda47d17bf7d6e66acade1a9d9078e46ed7ae8d8ce3784dfd9c9712281ff6fc8c9623e8b018deb9771ca5c00b354aa7b13df0d9454980f39215db2e223567f7188335c50c2b3a2bdeb78eff0c1951e10ff2fd012fe0ed0deca38b759bae29c39392af764bc4124b564bb71d078bb4c6854a2; _gcl_au=1.1.1191937899.1614844870; sc=EA1A72FD-DF88-AD2B-1D52-11AEF89C9E8E; _ga_FTJDFPLD2Q=GS1.1.1614854046.3.1.1614855203.59; _ga=GA1.2.1282539681.1614844871; BX_USER_ID=73fe847f4e396ac84b09eb93117ea8ed; _gid=GA1.2.1926838302.1614844872; _hjid=523afe21-edf0-4931-b234-ee1e89186e7d; _fbp=fb.1.1614844872514.1271315929; BITRIX_SM_SALE_UID=541265190; banner1=true; epic_digital_sid=1fad07f88c4e3df561641124728ba709; __cf_bm=216924ed7a1e9500caf805008011d06368c89486-1614854858-1800-AYC1DG2zPx9S45VQmYaTn1nl1O+5TIT0ReJFIdJdjwy/s0ayQ/HTPtpHLOcatCm3KMWPw7xCKbTSkV/cAMAYSFY='}

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
        print("Папка уже существует!")
    else:
        os.mkdir(FOLDER_NAME)

    with open(filename, 'w') as f:
        json.dump(data, f, **kwargs)


def dump_to_csv(file_name, data):
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
    pagination = soup.find_all('a', class_='custom-pagination__item')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def crawl_categories(URL):
    """Собирает ссылки на КАТЕГОРИИ"""
    cat_urls = []
    res = get_req(URL)
    soup = get_soup(res)

    categories_yes_no = soup.find('div', class_='shop-categories')
    if categories_yes_no:
        try:
            categoris_title = soup.find('h1', class_='shop-categories__title nc')
            categoris_title = categoris_title.text.strip()
            all_categories_hrefs = soup.find_all('section', class_='shop-categories__item')
            for tag in all_categories_hrefs:
                href = tag.find('div', class_='shop-categories__item-link')
                href = href.find('a', class_='shop-categories__item-title nc')
                href = href.get('href')
                url = '{}'.format(href)
                cat_urls.append(url)
            sleep(random.randrange(2, 4))
            print(f'\nВ категории "{categoris_title}" скопировано {len(cat_urls)} URLs адресов.')

            return cat_urls

        except Exception:
            print('Error categories')
    else:
        print('')


def crawl_products(cat_urls):
    """Собирает со страниц ссылки на товары"""
    urls = []

    if cat_urls is None:
        cat_urls = URL

        try:
            res = get_req(cat_urls)
        except Exception:
            print('битый URLs')

        soup = get_soup(res)
        pages_count = get_page_count(soup)

        group_cat = soup.find('h1', class_='nc').text.strip()
        print(f'\tВ группе "{group_cat}" - {pages_count}стр.')

        for page_n in range(1, 1 + pages_count):
            print(f'\tСтраница {page_n} из {pages_count}...')
            res = get_req(cat_urls, params={'PAGEN_1': page_n})
            soup = get_soup(res)

            all_products_hrefs = soup.find_all('div', class_='columns product-Wrap card-wrapper')
            for tag in all_products_hrefs:
                price_yes_no = tag.find('div', class_='card__price')
                price_yes_no = price_yes_no.find('span', class_='card__price-sum')
                if price_yes_no is None:
                    break   # print('Нет в наличии')
                else:
                    href = tag.find('div', class_='card__name')
                    href = href.find('a', class_='custom-link custom-link--big custom-link--inverted custom-link--blue')
                    href = href.get('href')
                    url = '{}'.format(href)
                    urls.append(url)
        sleep(random.randrange(2, 4))

        print(f'\nВсего URLs с товаром - {len(urls)} скопировано\n')

        return urls

    else:

        cat_urls = cat_urls

        pages_count_cat_urls = 1

        for url in cat_urls:
            try:
                res = get_req(url)
            except Exception:
                print('битый URLs')
                break

            soup = get_soup(res)
            pages_count = get_page_count(soup)

            group_cat = soup.find('h1', class_='nc').text.strip()
            print(f'\nКатегория: URL - {pages_count_cat_urls} из {len(cat_urls)}...')
            pages_count_cat_urls += 1
            print(f'\tВ группе "{group_cat}" - {pages_count}страниц')

            for page_n in range(1, 1 + pages_count):
                print(f'\tСтраница {page_n} из {pages_count}...')
                res = get_req(url, params={'PAGEN_1': page_n})
                soup = get_soup(res)

                all_products_hrefs = soup.find_all('div', class_='columns product-Wrap card-wrapper')
                for tag in all_products_hrefs:
                    price_yes_no = tag.find('div', class_='card__price')
                    price_yes_no = price_yes_no.find('span', class_='card__price-sum')
                    if price_yes_no is None:
                        break   # print('Нет в наличии')
                    else:
                        href = tag.find('div', class_='card__name')
                        href = href.find('a', class_='custom-link custom-link--big custom-link--inverted custom-link--blue')
                        href = href.get('href')
                        url = '{}'.format(href)
                        urls.append(url)
            sleep(random.randrange(2, 4))

        print(f'\nВсего URLs с товаром - {len(urls)} скопировано\n')

        return urls


def parse_products(urls):
    """Парсинг полей по каждому товару"""
    data = []

    count = 0
    iteration_count = len(urls)

    for url in urls:
        res = get_req(url)
        soup = get_soup(res)
        try:
            brend = soup.find('div', class_='p-block__row p-block__row--char')
            brend = brend.find('a', class_='p-char__brand')
            brend = brend['title'].strip()
        except Exception:
            brend = ''

        try:
            art = soup.find('div', class_='p-block__code nc')
            art = art.text.strip().replace('КОД ', '').replace('КОД', '')
        except Exception:
            art = ''

        try:
            name = soup.find('header', class_='p-block p-block--header p-header')
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
            break

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

        sleep(random.randrange(2, 4))

        count += 1
        iteration_count = iteration_count - 1
        print(f"Итерация #{count} завершена, осталось итераций #{iteration_count}")
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

    sleep(random.randrange(2, 4))

    return data


def main():
    cat_urls = crawl_categories(URL)
    urls = crawl_products(cat_urls)
    data = parse_products(urls)
    dump_to_json(OUT_JSON_FILENAME, data)
    dump_to_csv(OUT_CSV_FILENAME, data)


if __name__ == '__main__':
    main()
