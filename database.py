from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///media.db", echo=False)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT COLLATE NOCASE,
            type TEXT,
            year INTEGER,
            genre TEXT,
            UNIQUE(title, type, year)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS item_directors (
            item_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (item_id, person_id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS item_actors (
            item_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (item_id, person_id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            date_of_review DATE,
            rating INTEGER,
            review TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            UNIQUE(user_id, item_id)
        );
        """))

        conn.commit()