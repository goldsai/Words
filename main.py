import string
import urllib.parse as URL
from bs4 import BeautifulSoup
import requests
import sqlite3 as sq
from pathlib import Path


def get_page(url: str) -> requests.Response:
    """
    """
    headers = {
        "Accept": "*/*",
        "Accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }

    return requests.get(url, headers=headers)


def parse_url(url: str):
    u = URL.urlparse(url)
    path = u.path
    base = url[:url.index(path)]
    t_url = u.geturl()
    index_sharp = t_url.find('#')
    if index_sharp > -1:
        t_url = t_url[:index_sharp]
    # print(f'{t_url=}')
    # print(f'{path=}')
    # print(f'{base=}')
    # print(f'{u.fragment=}')
    # print(f'{u.geturl()=}')
    # print(f'{u.hostname=}')
    # print(f'{u.netloc=}')
    # print(f'{u.params=}')
    # print(f'{u.password=}')
    # print(f'{u.path=}')
    # print(f'{u.port=}')
    # print(f'{u.query=}')
    # print(f'{u.scheme=}')
    # print(f'{u.username=}')
    index_slesh = path.rfind('/')
    if index_slesh > -1:
        file_name_ext = path[index_slesh+1:]

        path = path[:index_slesh+1]

        index_dot = file_name_ext.rfind('.')
        if index_dot > -1:
            file_name = file_name_ext[0:index_dot]
            ext = file_name_ext[index_dot+1:]
        else:
            file_name = file_name_ext
            ext = ''

        return (t_url, base, path, file_name_ext, file_name, ext)
    return('', '', '', '', '', '')


def add_word(word: str, dict_words) -> None:
    norm_word = _normalization_word(word)
    if norm_word is not None:
        if norm_word in dict_words:
            dict_words[norm_word] += 1
        else:
            dict_words[norm_word] = 1
    # print(norm_word)


def _normalization_word(word: str) -> str:
    str = word.strip(string.punctuation).capitalize()
    if str.isalpha():
        return str


def sort_words(word_count: dict):
    l = sorted(word_count.items())
    return {k: v for k, v in sorted(l, key=lambda item: item[1], reverse=True)}


def init_db(cur: sq.Cursor):
    cur.executescript("""
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS "words" (
    "id_word"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "word"      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "pages" (
    "id_page"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "url"       TEXT NOT NULL,
    "marker"    NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS "sentences" (
    "id_sent"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "sent"      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "sent_in_page" (
    "id_page"   INTEGER NOT NULL,
    "id_sent"   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "words_in_page" (
    "id_page"   INTEGER NOT NULL,
    "id_word"   INTEGER NOT NULL,
    "count"     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS "words_in_sent" (
    "id_sent"   INTEGER NOT NULL,
    "id_word"   INTEGER NOT NULL
);

COMMIT;

    """)


def add_page(cur: sq.Cursor, url: str):
    pass


def add_word_in_db(cur: sq.Cursor, id_page, page_words: dict):
    pass


def add_sentences(cur: sq.Cursor, id_page, sentences: list[str]):
    pass


if __name__ == '__main__':
    url = 'https://docs.python.org/3.11/reference/index.html?d=45#24'

    (t_url, base, path, page_name, file_name, ext) = parse_url(url)

    text = get_page(url).text
    soup = BeautifulSoup(text, 'lxml')

    sentences = soup.get_text().splitlines()
    # print(l)
    # print(len(l))
    # exit()
    l = soup.get_text().split()

    # print(l)
    # print(len(l))

    page_words = {}
    for txt in l:
        add_word(txt, page_words)

    page_words = sort_words(page_words)

    # print(page_words)
    # print(len(page_words))
    # print(path, page_name, file_name, ext, sep="\n")

    path_db = Path(__file__).parent/'words.db'
    # print(path_db)
    # print(__file__)
    with sq.connect(path_db) as con:
        cur = con.cursor()
        init_db(cur)

        id_page = add_page(cur, t_url)
        add_word_in_db(cur, id_page, page_words)
        add_sentences(cur, id_page, sentences)
