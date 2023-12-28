import streamlit as st
import streamlit_authenticator as stauth
from firebase_admin import db, credentials

# -- AUTHENTICATE USING DB ---
def load_user_auth(cred_ref: str, cookie_ref: str):
    credentials = db.reference(cred_ref).get()
    cookie = db.reference(cookie_ref).get()
    authenticator = stauth.Authenticate(
        credentials,
        cookie['name'],
        cookie['key'],
        cookie['expiry_days'],
        cookie['preauthorized'],
        )
    return authenticator
