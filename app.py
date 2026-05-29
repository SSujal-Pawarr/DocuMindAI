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

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)


def auth_page():
    st.title("DocuMind AI")
    tab1,tab2 = st.tabs(["Login","Register"])

    with tab1:
        u=st.text_input("Username")
        p=st.text_input("Password",type="password")
        if st.button("Login"):
            user=users.find_one({"username":u})
            if user and check_password(p, user["password"]):
                st.session_state.user = u
                st.session_state.history = []
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        ru=st.text_input("New Username")
        rp=st.text_input("New Password",type="password")
        if st.button("Register"):
            if users.find_one({"username": ru}):
               st.error("Username already exists")
            else:
                users.insert_one({"username": ru, "password": hash_password(rp)})    
                st.success("Registered")

def chat_page():
    st.title("DocuMind AI")
    

    col1,col2 = st.columns([3,1])
    col1.write(f"User: {st.session_state.user}")
    if col2.button("Logout"):
        st.session_state.user = ""
        st.session_state.history = []
        st.rerun()

    file = st.file_uploader("Upload PDF", type="pdf")
    if file:
        text = ""
        with pdfplumber.open(file) as pdf:
            