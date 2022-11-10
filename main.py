from datetime import datetime
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


def get_words(words: list[str]) -> dict:
    count_words = {}
    for txt in words:
        add_word(txt, count_words)
    return count_words


def add_word(word: str, dict_words) -> None:
    norm_word = _normalization_word(word)
    if norm_word is not None:
        if norm_word in dict_words:
            dict_words[norm_word]['count'] += 1
        else:
            dict_words[norm_word] = {'count': 1}
    # print(norm_word)


def _normalization_word(word: str) -> str:
    str = word.strip(string.punctuation).capitalize()
    if str.isalpha():
        return str


def sort_words(word_count: dict):
    l = sorted(word_count.items())
    return {k: v for k, v in sorted(l, key=lambda item: item[1]['Count'], reverse=True)}


def init_db(cur: sq.Cursor):
    cur.executescript("""
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS "words" (
    "id_word"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "word"      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ind_words ON words (word);

CREATE TABLE IF NOT EXISTS "pages" (
    "id_page"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "url"       TEXT NOT NULL,
    "marker"    NOT NULL DEFAULT 0
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
CREATE INDEX IF NOT EXISTS ind_words_in_page ON words_in_page (id_page, id_word);

CREATE TABLE IF NOT EXISTS "words_in_sent" (
    "id_sent"   INTEGER NOT NULL,
    "id_word"   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ind_words_in_sent ON words_in_sent (id_sent, id_word);

COMMIT;

    """)


def _get_sets_words(line: str) -> set:
    rez = set()
    for item in line.split():
        word = _normalization_word(item)
        if word:
            rez.add(word)
    return rez


def _normalization_sentences(line: str):
    line = line.strip()

    return {'line': line, 'words': _get_sets_words(line)} if line else None


def get_sentences(soap: BeautifulSoup) -> list[dict]:
    l = []
    for line in soup.get_text().splitlines():
        if item := _normalization_sentences(line):
            l.append(item)
    return l


# def parser_sql_url(url) -> str:
#     check_list = [
#         ';',
#         'SELECT',
#         ''
#     ]


def add_page(cur: sq.Cursor, url: str):
    # cur.execute("SELECT id_page FROM pages WHERE url LIKE '?'", (url,))
    cur.execute("SELECT id_page FROM pages WHERE url LIKE ?", (url,))
    rez = cur.fetchone()
    if rez:

        return True, rez[0]
    else:
        cur.execute("INSERT INTO pages (url) VALUES (?)", (url,))

        return False, cur.lastrowid


def get_id_word(cur: sq.Cursor, word: str):
    cur.execute("SELECT id_word FROM words WHERE word LIKE ?", (word,))
    rez = cur.fetchone()
    if rez:

        return rez[0]
    else:
        cur.execute("INSERT INTO words (word) VALUES (?)", (word,))

        return cur.lastrowid


def add_word_in_db(cur: sq.Cursor, id_page, page_words: dict):
    for word, item in page_words.items():
        id_word = get_id_word(cur, word)
        count = item['count']
        cur.execute(
            "SELECT 'count', rowid FROM words_in_page WHERE id_page = ? AND id_word = ?", (id_page, id_word))
        rez = cur.fetchone()
        if rez:
            item['id'] = cur.lastrowid
            if rez[0] != count:
                cur.execute(
                    "UPDATE words_in_page SET 'count' = ? WHERE rowid = ?", (count, rez[1]))

        else:
            cur.execute(
                "INSERT INTO words_in_page (id_page, id_word, 'count') VALUES (?, ?, ?)", (id_page, id_word, count))
            item['id'] = cur.lastrowid


def get_id_sentences(cur: sq.Cursor, sent: str):

    cur.execute("SELECT id_sent FROM sentences WHERE sent LIKE ?", (sent,))
    rez = cur.fetchone()
    if rez:

        return True, rez[0]
    else:
        cur.execute("INSERT INTO sentences (sent) VALUES (?)", (sent,))

        return False, cur.lastrowid


def add_to_db_sent(cur: sq.Cursor, id_page, id_sent):
    # sent_in_page
    cur.execute(
        "SELECT rowid FROM sent_in_page WHERE id_page = ? AND id_sent = ?", (id_page, id_sent))
    rez = cur.fetchone()
    if rez:

        return rez[0]
    else:
        cur.execute(
            "INSERT INTO sent_in_page (id_page, id_sent) VALUES (?, ?)", (id_page, id_sent))

        return cur.lastrowid


def add_word_in_sent(cur, id_sent, id_word):
    cur.execute(
        "SELECT rowid FROM words_in_sent WHERE id_sent = ? AND id_word = ?", (id_sent, id_word))
    rez = cur.fetchone()
    if rez:

        return rez[0]
    else:
        cur.execute(
            "INSERT INTO words_in_sent (id_sent, id_word) VALUES (?, ?)", (id_sent, id_word))

        return cur.lastrowid


def add_sentences(cur: sq.Cursor, id_page, sentences: list[str], page_words: dict):
    for sent in sentences:
        is_sent, id_sent = get_id_sentences(cur, sent['line'])
        add_to_db_sent(cur, id_page, id_sent)
        if not is_sent:
            for word in sent['words']:
                id_word = page_words[word]['id']
                # words_in_sent
                add_word_in_sent(cur, id_sent, id_word)


def add_new_urls(url: str, soup: BeautifulSoup = None, list_urls: list[str] = None) -> None:
    """add_new_urls добавляет новые ссылки в список

    url - должен быть полный, используется для обработки относительных ссылок.
          если page == None, то этот адрес используется для загрузки страницы

    Args:
        url (str): адрес страницы для поиска ссылок
        page (BeautifulSoup): страница BeautifulSoup для поиска ссылок
        list_urls (list[str]): список для добавления новых ссылок
    """
    page = soup if soup else get_page(url)
    # ToDo: Необходимо проверить тег meta base, который может изменить путь для относительных ссылок
    base_netloc = URL.urlsplit(url).netloc

    list_url = list_urls if list_urls else []

    for link in page.find_all('a'):
        href = link.get('href')
        new_url = URL.urldefrag(URL.urljoin(url, href, True)).url

        if base_netloc == URL.urlsplit(new_url).netloc and parse_url(new_url)[5].lower() in ('html', 'htm') and not new_url in list_url:
            list_url.append(new_url)


if __name__ == '__main__':
    # list_url
    # Общее время: 2:23:45.436385 - 267 страниц
    list_url = ['https://docs.python.org/3.11/reference/index.html']
    global_time = datetime.now()
    count_url = 0
    error_url = []
    max_loop_time = None
    min_loop_time = None
    m_one = True
    while count_url < len(list_url):
        time_loop = datetime.now()
        url = list_url[count_url]
        print(
            f'Обработка:\t{url}\n\t\tОбработал: {count_url} ссылок. \n\t\tОсталось: {len(list_url)-count_url} ссылок')
        count_url += 1
        try:
            (t_url, base, path, page_name, file_name, ext) = parse_url(url)

            text = get_page(url).text
            soup = BeautifulSoup(text, 'lxml')

            add_new_urls(url, soup, list_url)

            sentences = get_sentences(soup)

            words = soup.get_text().split()

            page_words = get_words(words)

            path_db = Path(__file__).parent/'words.db'

            print(
                f'\t\tОбработал {len(page_words)} слов; {len(sentences)} предложения за {datetime.now()-time_loop}')
        except Exception as e:

            print('-'*50)
            print(f'При обработке ссылки "{url}" произошло исключение {e}')
            print('-'*50)
            error_url.append({'url': url, 'err': e})
        else:
            time_db = datetime.now()
            with sq.connect(path_db) as con:
                cur = con.cursor()
                if m_one:
                    init_db(cur)
                    m_one = False

                in_db, id_page = add_page(cur, t_url)
                if not in_db:
                    add_word_in_db(cur, id_page, page_words)
                    add_sentences(cur, id_page, sentences, page_words)
            print(
                f'\t\tРабота с БД за:{datetime.now()-time_db}')
            # print(f'\t\tОбработал {len(page_words)} слов')
        _time_loop = datetime.now()-time_loop
        if not min_loop_time:
            min_loop_time = _time_loop
            max_loop_time = _time_loop
        if max_loop_time < _time_loop:
            max_loop_time = _time_loop
        if min_loop_time > _time_loop:
            min_loop_time = _time_loop
        print(
            f'\t\tОбработал за:{_time_loop} ({min_loop_time}:{max_loop_time})\n')
    print(
        f'\nОбщее время: {datetime.now()-global_time} \n\tВсего обработал: {count_url} ссылок')

    print(f'Необработанно {len(error_url)} ссылок:')
    for num, url in enumerate(error_url):
        print(f'{num}\t - {url}')
