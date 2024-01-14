import streamlit as st
import firebase_admin
from firebase_admin import db, credentials
from db_module import *
from auth_module import *
import streamlit_authenticator as stauth # pip install streamlit-authenticator


# -- DB AUTHENTICATION
db_creds = dict(st.secrets['firebase']['db_access'])
@st.cache_resource # cache the initializing of the db
def load_db():
    cred = credentials.Certificate(db_creds)
    return firebase_admin.initialize_app(cred, {"databaseURL":st.secrets['firebase']['url']})


# Setup config - to configure title of webpage
st.set_page_config(page_title='Projekt overblik', page_icon="🧪",)
app = load_db()

# --- USER AUTHENTICATION ---
# Load the authenticator from the load_user_auth function in the auth_module.py
# cred_ref is the db reference to the credentials, cookie_ref is the reference to the cookie settings in the db
authenticator = load_user_auth(cred_ref="/credentials/", cookie_ref="/cookie")


# User and authentication status
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")
if authentication_status == None:
    st.warning("Please enter username and password")

if authentication_status and username != "admin":
    # --- USER ACCESS
    # --- SIDEBAR ---
    authenticator.logout("Logout", "sidebar")


    # --- TITLE ---
    st.title("User settings")


    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                new_user_credentials = authenticator.credentials.get("usernames").get(st.session_state["username"])
                ref= db.reference(f"/credentials/usernames/{st.session_state['username']}")
                ref.update(new_user_credentials)
                st.success('Passord er ændret')

        except Exception as e:
            st.error(e)

    st.stop()

    # --- FOTTER ---
