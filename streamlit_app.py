import streamlit as st
from database import init_db

st.set_page_config(page_title="Media Ratings", layout="wide")

init_db()

st.title("Media Rating App")
st.write("Database initialized.")
