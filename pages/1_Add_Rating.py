import streamlit as st
from sqlalchemy import text
from database import engine
import datetime

st.title("Add Item + Rating")

# --- USER ---
username = st.text_input("Username")

# --- ITEM INFO ---
title = st.text_input("Title")
media_type = st.selectbox("Type", ["movie", "tv", "music", "book"])
year = st.number_input("Year", min_value=0, max_value=datetime.datetime.now().year, step=1)
genre = st.text_input("Genre")

# --- PEOPLE (comma separated for now) ---
# --- DIRECTORS ---
st.subheader("Directors")

if "directors" not in st.session_state:
    st.session_state.directors = [""]

def add_director():
    st.session_state.directors.append("")

def remove_director(index):
    st.session_state.directors.pop(index)

for i in range(len(st.session_state.directors)):
    cols = st.columns([4,1])
    st.session_state.directors[i] = cols[0].text_input(
        f"Director {i+1}",
        value=st.session_state.directors[i],
        key=f"director_{i}"
    )
    if cols[1].button("X", key=f"remove_director_{i}"):
        remove_director(i)
        st.rerun()

st.button("Add Director", on_click=add_director)

directors = [d.strip() for d in st.session_state.directors if d.strip()]

# --- ACTORS ---
st.subheader("Actors")

if "actors" not in st.session_state:
    st.session_state.actors = [""]

def add_actor():
    st.session_state.actors.append("")

def remove_actor(index):
    st.session_state.actors.pop(index)

for i in range(len(st.session_state.actors)):
    cols = st.columns([4,1])
    st.session_state.actors[i] = cols[0].text_input(
        f"Actor {i+1}",
        value=st.session_state.actors[i],
        key=f"actor_{i}"
    )
    if cols[1].button("X", key=f"remove_actor_{i}"):
        remove_actor(i)
        st.rerun()

st.button("Add Actor", on_click=add_actor)

actors = [a.strip() for a in st.session_state.actors if a.strip()]

# --- RATING ---
rating = st.slider("Rating", 1, 10)
review = st.text_area("Review")

if st.button("Submit"):

    if not username or not title:
        st.error("Username and title are required.")
        st.stop()

    with engine.begin() as conn:

        # --- USER ---
        conn.execute(text("""
            INSERT OR IGNORE INTO users (username)
            VALUES (:username)
        """), {"username": username})

        user_id = conn.execute(text("""
            SELECT id FROM users WHERE username = :username
        """), {"username": username}).scalar_one()

        # --- ITEM ---
        conn.execute(text("""
            INSERT OR IGNORE INTO items (title, type, year, genre)
            VALUES (:title, :type, :year, :genre)
        """), {
            "title": title,
            "type": media_type,
            "year": year,
            "genre": genre
        })

        item_id = conn.execute(text("""
            SELECT id FROM items
            WHERE title=:title AND type=:type AND year=:year
        """), {
            "title": title,
            "type": media_type,
            "year": year
        }).scalar_one()

        # --- DIRECTORS ---
        for director in directors:
            conn.execute(text("""
                INSERT OR IGNORE INTO people (name)
                VALUES (:name)
            """), {"name": director})

            person_id = conn.execute(text("""
                SELECT id FROM people WHERE name=:name
            """), {"name": director}).scalar_one()

            conn.execute(text("""
                INSERT OR IGNORE INTO item_directors (item_id, person_id)
                VALUES (:item_id, :person_id)
            """), {
                "item_id": item_id,
                "person_id": person_id
            })

        # --- ACTORS ---
        for actor in actors:
            conn.execute(text("""
                INSERT OR IGNORE INTO people (name)
                VALUES (:name)
            """), {"name": actor})

            person_id = conn.execute(text("""
                SELECT id FROM people WHERE name=:name
            """), {"name": actor}).scalar_one()

            conn.execute(text("""
                INSERT OR IGNORE INTO item_actors (item_id, person_id)
                VALUES (:item_id, :person_id)
            """), {
                "item_id": item_id,
                "person_id": person_id
            })

        # --- RATING ---
        conn.execute(text("""
            INSERT OR REPLACE INTO ratings (user_id, item_id, rating, review)
            VALUES (:user_id, :item_id, :rating, :review)
        """), {
            "user_id": user_id,
            "item_id": item_id,
            "rating": rating,
            "review": review
        })

    st.success("Entry saved successfully.")