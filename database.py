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
            type TEXT,
            title TEXT,
            year INTEGER,
            genre TEXT,
            unique(title, genre, year)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS people_directors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS people_actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id TEXT
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            rating INTEGER,
            review TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            unique(item_id, user_id)
        );
        """))

        conn.commit()