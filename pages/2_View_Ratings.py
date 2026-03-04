import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine

st.title("All Media")

query = """
    SELECT 
        i.id,
        i.title,
        i.type,
        i.year,
        i.genre,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.rating) AS rating_count,

        GROUP_CONCAT(DISTINCT d.name) AS directors,
        GROUP_CONCAT(DISTINCT a.name) AS actors

    FROM items i

    LEFT JOIN ratings r ON i.id = r.item_id

    LEFT JOIN item_directors idr ON i.id = idr.item_id
    LEFT JOIN people d ON idr.person_id = d.id

    LEFT JOIN item_actors ia ON i.id = ia.item_id
    LEFT JOIN people a ON ia.person_id = a.id

    GROUP BY i.id
    ORDER BY avg_rating DESC
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

st.dataframe(df, width='stretch')