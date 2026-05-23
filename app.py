import streamlit as st
from pymongo import MongoClient
import bcrypt
import pdfplumber
import requests

client = MongoClient("mongodb://localhost:27017/")
d=client["ai_app"]
users=db["users"]
docs=db["documents"]

if "user" not in st.session.state:
    st.session_state.user = ""
if "history" not in st.session.state:
    st.session_state.history = []

st.set_page_config(page_title="DocuMind App")


def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

