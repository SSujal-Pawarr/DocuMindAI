import streamlit as st
from pymongo import MongoClient
import bcrypt
import pdfplumber
import requests


# ---------------- MongoDB ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_app"]

users = db["users"]
docs = db["documents"]

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="DocuMind App")

# ---------------- Session State ----------------
if "user" not in st.session_state:
    st.session_state.user = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- Password Functions ----------------
def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)

# ---------------- Authentication Page ----------------
def auth_page():
    st.title("DocuMind AI")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = users.find_one({"username": u})

            if user and check_password(p, user["password"]):
                st.session_state.user = u
                st.session_state.history = []
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")

        if st.button("Register"):
            if users.find_one({"username": ru}):
                st.error("Username already exists")
            else:
                users.insert_one({
                    "username": ru,
                    "password": hash_password(rp)
                })
                st.success("Registered Successfully")


# ---------------- Chat Page ----------------
def chat_page():
    st.title("DocuMind AI")

    col1, col2 = st.columns([3, 1])

    col1.write(f"User: {st.session_state.user}")

    if col2.button("Logout"):
        st.session_state.user = ""
        st.session_state.history = []
        st.rerun()

    # PDF Upload
    file = st.file_uploader("Upload PDF", type="pdf")

    if file:
        text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # Replace old document for user
        docs.delete_many({"user": st.session_state.user})

        docs.insert_one({
            "user": st.session_state.user,
            "content": text
        })

        st.success("PDF Processed Successfully")

    # Chat History
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Question
    q = st.chat_input("Ask something about your document...")

    if q:
        st.session_state.history.append({
            "role": "user",
            "content": q
        })

        doc = docs.find_one({"user": st.session_state.user})

        if not doc:
            ans = "Please upload a document first."

        else:
            content = doc["content"][:3000]

            try:
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer YOUR_GROQ_API_KEY",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Answer only from the provided document context."
                            },
                            {
                                "role": "user",
                                "content": f"{content}\n\nQuestion: {q}"
                            }
                        ]
                    }
                )

                ans = res.json()["choices"][0]["message"]["content"]

            except Exception as e:
                ans = f"Error: {str(e)}"

        st.session_state.history.append({
            "role": "assistant",
            "content": ans
        })

        st.rerun()

# ---------------- Main ----------------
if st.session_state.user:
    chat_page()
else:
    auth_page()