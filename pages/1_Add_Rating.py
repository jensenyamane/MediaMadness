import streamlit as st
from sqlalchemy import text
from database import engine
import datetime

st.title("Add Item + Rating")

# Clear form state if success message was just shown
if st.session_state.get("show_success"):
    st.success("Entry saved successfully.")
    st.session_state["show_success"] = False

# --- USER ---
username = st.text_input("Username", key="username_input")

# --- ITEM INFO ---
title = st.text_input("Title", key="title_input")

existing_items_query = """
SELECT id, title, year, genre
FROM items
WHERE LOWER(title) = LOWER(:title)
"""

with engine.begin() as conn:
    matches = conn.execute(
        text(existing_items_query),
        {"title": title}
    ).fetchall()

    item_data = None  # default if no match

    if matches:
        options = {f"{row.title} ({row.year})": row.id for row in matches}

        st.warning("⚠ Existing title found. Select below or create a new entry.")
        selected = st.selectbox(
            "Existing entries found. Select one or create new:",
            ["Create New"] + list(options.keys()),
            key="existing_select"
        )

        if selected != "Create New":
            selected_item_id = options[selected]
            item_data = conn.execute(
                text("SELECT * FROM items WHERE id=:id"),
                {"id": selected_item_id}
            ).mappings().fetchone()  # use .mappings() for dict-like access

            # Save existing title but don't show a duplicate input
            title = item_data["title"] if item_data else title

            # Prefill directors and actors from DB for the selected item
            directors_rows = conn.execute(text("""
                SELECT p.name FROM people p
                JOIN item_directors id ON p.id = id.person_id
                WHERE id.item_id = :item_id
            """), {"item_id": selected_item_id}).fetchall()
            prefill_directors = [r[0] for r in directors_rows] if directors_rows else []

            actors_rows = conn.execute(text("""
                SELECT p.name FROM people p
                JOIN item_actors ia ON p.id = ia.person_id
                WHERE ia.item_id = :item_id
            """), {"item_id": selected_item_id}).fetchall()
            prefill_actors = [r[0] for r in actors_rows] if actors_rows else []

            # Initialize or replace session_state lists when selection changes
            if ("_last_selected" not in st.session_state) or (st.session_state.get("_last_selected") != selected_item_id):
                st.session_state.directors = prefill_directors if prefill_directors else [""]
                st.session_state.actors = prefill_actors if prefill_actors else [""]
                st.session_state["_last_selected"] = selected_item_id
                # Mirror values into individual widget keys so text_input shows them
                for idx, name in enumerate(st.session_state.directors):
                    st.session_state[f"director_{idx}"] = name
                for idx, name in enumerate(st.session_state.actors):
                    st.session_state[f"actor_{idx}"] = name

            media_type = st.selectbox(
                "Type",
                ["movie", "tv", "music", "book"],
                index=["movie", "tv", "music", "book"].index(item_data["type"]) if item_data else 0,
                key="media_type_existing"
            )

            year = st.number_input(
                "Year",
                min_value=1900,
                max_value=2100,
                value=item_data["year"] if item_data else 2026
            )

            genre = st.text_input(
                "Genre",
                value=item_data["genre"] if item_data else "",
                key="genre_input_existing"
            )
        else:
            # "Create New" chosen: reset director/actor session state
            if "directors" in st.session_state:
                st.session_state.directors = [""]
                st.session_state["director_0"] = ""
            if "actors" in st.session_state:
                st.session_state.actors = [""]
                st.session_state["actor_0"] = ""
            if "_last_selected" in st.session_state:
                del st.session_state["_last_selected"]


if item_data:
    # Existing item selected: use the prefilled media_type, year, genre above (don't render duplicates)
    pass
else:
    media_type = st.selectbox("Type", ["movie", "tv", "music", "book"], key="media_type_new", index=None)
    year = st.number_input("Year", min_value=0, max_value=datetime.datetime.now().year, value=2026, step=1, key="year_input")
    genre = st.text_input("Genre", key="genre_input_new")

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
        key=f"actor_{i}"
    )
    if cols[1].button("X", key=f"remove_actor_{i}"):
        remove_actor(i)
        st.rerun()

st.button("Add Actor", on_click=add_actor)

actors = [a.strip() for a in st.session_state.actors if a.strip()]

# --- RATING ---
rating = st.slider("Rating", 0.0, 10.0, value=5.0, step=0.5, format="%.1f", key="rating_input")
review = st.text_area("Review", key="review_input")

# Submit and Reset buttons side-by-side
col1, col2 = st.columns(2)

def reset_form():
    st.session_state["username_input"] = ""
    st.session_state["title_input"] = ""
    st.session_state["genre_input_existing"] = ""
    st.session_state["genre_input_new"] = ""
    st.session_state["review_input"] = ""
    st.session_state["rating_input"] = 5.0
    st.session_state["year_input"] = datetime.datetime.now().year
    st.session_state["media_type_new"] = "movie"
    st.session_state["media_type_existing"] = ""
    st.session_state["existing_select"] = "Create New"
    st.session_state.directors = [""]
    st.session_state.actors = [""]
    st.session_state["director_0"] = ""
    st.session_state["actor_0"] = ""
    if "_last_selected" in st.session_state:
        del st.session_state["_last_selected"]

with col1:
    submit_button = st.button("Submit")
with col2:
    st.button("Reset Form", on_click=reset_form)

if submit_button:

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

    # Set flag to show success on next render, then rerun
    st.session_state["show_success"] = True
    st.rerun()