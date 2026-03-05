import streamlit as st
from database import init_db

st.set_page_config(page_title="Media Ratings", layout="wide")

init_db()

st.title("Media Madness")
st.write('This app was made on Streamlit. They let us do this for free, but this first page has to be called "streamlit app". '
         'I guess it\'s their version of a watermark. Anyways, click any of the other options to get started.')