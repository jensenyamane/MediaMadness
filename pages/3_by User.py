import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine

st.title("Ratings by User")

# Get all users for dropdown
with engine.connect() as conn:
    users_result = conn.execute(text("SELECT username FROM users ORDER BY username"))
    users = [row[0] for row in users_result.fetchall()]

# Get all media types
# media_types = ["movie", "tv", "music", "book"]
media_types = ["movie"]

# User selection
selected_user = st.selectbox("Select User", users, key="user_select")

# Media type selection
selected_media_type = st.selectbox("Select Media Type", media_types, key="media_type_select")

# Only show results if both are selected
if selected_user and selected_media_type:
    st.subheader(f"{selected_user}'s Top {selected_media_type.title()} Ratings")

    # Query for user's ratings of selected media type
    query = """
        SELECT 
            i.title,
            i.year,
            i.genre,
            r.rating,
            r.review,
            GROUP_CONCAT(DISTINCT d.name) AS directors,
            GROUP_CONCAT(DISTINCT a.name) AS actors
        FROM ratings r
        JOIN items i ON r.item_id = i.id
        LEFT JOIN item_directors idr ON i.id = idr.item_id
        LEFT JOIN people d ON idr.person_id = d.id
        LEFT JOIN item_actors ia ON i.id = ia.item_id
        LEFT JOIN people a ON ia.person_id = a.id
        WHERE r.user_id = (SELECT id FROM users WHERE username = :username)
        AND i.type = :media_type
        GROUP BY r.id, i.id
        ORDER BY r.rating DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"username": selected_user, "media_type": selected_media_type})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    if not df.empty:
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.write(f"No {selected_media_type} ratings found for {selected_user}.")