# Words

## Tables DB

### Words

| id_word | Word |

```SQL
CREATE TABLE IF NOT EXISTS "words" (
    "id_word"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "word"      TEXT NOT NULL
);
```

### Pages

| id_page | url | marker |

```SQL
CREATE TABLE IF NOT EXISTS "pages" (
    "id_page"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "url"       TEXT NOT NULL,
    "marker"    NOT NULL DEFAULT 1
);
```
### Sentences

| id_sentence | sentence |

```SQL
CREATE TABLE IF NOT EXISTS "sentences" (
    "id_sent"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "sent"      TEXT NOT NULL
);
```
### Sentences in page

| id_page | id_sentence |

```SQL
CREATE TABLE IF NOT EXISTS "sent_in_page" (
    "id_page"   INTEGER NOT NULL,
    "id_sent"   INTEGER NOT NULL
);
```
### Words in page

| id_page | id_word | count

```SQL
CREATE TABLE IF NOT EXISTS "words_in_page" (
    "id_page"   INTEGER NOT NULL,
    "id_word"   INTEGER NOT NULL
    "count"   INTEGER NOT NULL DEFAULT 1
);
```
### Words in sentence

| id_sentence | id_word |

```SQL
CREATE TABLE IF NOT EXISTS "words_in_sent" (
    "id_sent"   INTEGER NOT NULL
    "id_word"   INTEGER NOT NULL,
);
```