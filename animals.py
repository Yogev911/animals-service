from bs4 import BeautifulSoup
import requests
import re
import wikipedia
import traceback
import conf
import os
from multiprocessing import Pool


def preprocess_data(raw_text):
    """
    Eliminate brackets and parentheses from a string strip and lower
    :param raw_text: str
    :return: str
    """
    try:
        raw_text = raw_text.replace("?", "Unknown")
        raw_text = raw_text.replace(" or ", ", ")
        raw_text = raw_text.replace(" and ", ", ")
        raw_text = re.sub("\[.*?\]", "", raw_text)
        raw_text = re.sub("\(.*?\)", "", raw_text)
        return raw_text.strip().lower()
    except Exception as e:
        print(e.__str__())
        raise e


def get_tables():
    """
    Get list of table tag elements from URL
    :return: list [ bs4.element.Tag ]
    """
    page_html = requests.get(conf.PAGE_URL).text
    soup = BeautifulSoup(page_html, 'html.parser')
    tables = soup.find_all("table", {"class": conf.TABLE_CLASS_NAME})
    if not tables:
        raise ValueError("Table class not found")
    return tables


def parse_tables():
    tables = get_tables()
    body_tag = ''
    for table in tables:
        body_tag += "<br>"
        body_tag += parse_table(table)
    html_data = conf.HTML_TEMPLATE(body_tag)
    with open("index.html", 'w') as f:
        f.write(html_data)


def get_image_from_page(page_name):
    page = wikipedia.page(page_name)
    r = requests.get(page.images[0], stream=True)
    if r.status_code == 200:
        with open(conf.IMAGES_PATH + page.images[0].split('/')[-1], 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)


def parse_table(table):
    """
    Print clean parsed rows by configuration of given table
    :param table: bs4.element.Ta
    :return: None
    """
    rows = table.find_all('tr')
    if not rows:
        raise ValueError("No rows for table")
    pages = []
    table_tag = "<table>"
    tbl_headers = get_tbl_headers(rows)
    table_tag += "<tr>"
    for header in tbl_headers.keys():
        table_tag += conf.ADD_TH_TAG(header)
    table_tag += "</tr>"
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue
        for page_name in cols[0].find_all('a'):
            if not page_name:
                continue
            pages.append(page_name.text)
        table_tag += '<tr>'
        for header, col in tbl_headers.items():
            try:
                table_tag += f"<td>{preprocess_data(f'{header} : {cols[col].text}')} \t</td>"
            except IndexError:
                pass
        table_tag += '</tr>'
    table_tag += '</table>'
    if conf.DOWNLOAD_IMAGES:
        download_images(pages)
    return table_tag


def download_images(pages):
    """
    Download bulk of images via Pool
    :param pages: list [str]
    :return: None
    """
    try:
        pool = Pool(conf.MAX_PROCESS)
        pool.map_async(get_image_from_page, pages)
        pool.close()
        pool.join()
    except:
        pool.close()
        pool.join()


def get_tbl_headers(rows):
    """
    Get first row and extract headers cols
    :param rows:
    :return: dict
    """
    tbl_header = rows.pop(0)
    tbl_headers = {}
    for index, header_name in enumerate(tbl_header.find_all('th')):
        if header_name.text in conf.TABLE_HEADER_COLS:
            tbl_headers[header_name.text] = index
    return tbl_headers


if __name__ == '__main__':
    try:
        if not os.path.exists(conf.IMAGES_PATH):
            os.mkdir(conf.IMAGES_PATH)
        parse_tables()
    except requests.exceptions.MissingSchema as e:
        print(f"URL not valid, {e.__str__()}")
    except Exception as e:
        print(f"Failed parse page {e.__str__()}, {traceback.format_exc()}")
