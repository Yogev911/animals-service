from bs4 import BeautifulSoup
import requests
import re
import traceback
import conf


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
    for table in tables:
        parse_table(table)


def parse_table(table):
    """
    Print clean parsed rows by configuration of given table
    :param table: bs4.element.Ta
    :return: None
    """
    rows = table.find_all('tr')
    if not rows:
        raise ValueError("No rows for table")
    tbl_headers = get_tbl_headers(rows)
    for row in rows:
        line = ''
        cols = row.find_all('td')
        if not cols:
            continue
        for header, col in tbl_headers.items():
            try:
                line += f"{header} : {cols[col].text} \t"
            except IndexError:
                pass
        print(preprocess_data(line))


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
        parse_tables()
    except requests.exceptions.MissingSchema as e:
        print(f"URL not valid, {e.__str__()}")
    except Exception as e:
        print(f"Failed parse page {e.__str__()}, {traceback.format_exc()}")