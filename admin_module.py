# --- MODULES FOR ADMIN PANEL ---
import streamlit as st
import streamlit_authenticator as stauth
from firebase_admin import db, credentials
import time
from datetime import datetime, time as t
import json
import pandas as pd


# --- ADD USER TO DB ---
def add_user(name: str, users: list, password: list):
    if "admin" in name:
        st.error('Navne der indeholder "admin", er ikke tilladt!')
        return None
    if name in users:
        st.warning(f'{name} findes allerede')
        return None
    create_user_login(name, password):
    ref = db.reference(f"/content_container/usernames")
    user_template = {
        name.lower() :{
            "content":{
                "gruppekontrakt" :"",
                "problemformulering": "",
                "underemne": "Fremtidens skole",
                "undersøgelsesspørgsmål":""
                },
            "logbog": {
                "logbog for mandag": [
                    "",
                    ]
                },
            "graph" : {
                "data" : {
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}': 0,
                    }
                }
            }

        }
    ref.update(user_template)
    st.toast(f'{name.lower()} added')
    time.sleep(2)
    return True

def create_user_login(name: str, password: list):
    hashed_pass = stauth.Hasher(password).generate()
    ref = db.reference(f"/credentials/usernames")
    if name.lower() in ref.get():
        print("User exists")
        return None
    else:
        print("creating new user in db")
        login_template = {
            name.lower() : {
                "name": name.lower(),
                "password": hashed_pass[0]
                }
            }
        ref.update(login_template)
        return True

def remove_user(name: str):
    ref_cont = db.reference(f"/content_container/usernames/{name}")
    ref_cred = db.reference(f"/credentials/usernames/{name}")
    ref_cont.delete()
    ref_cred.delete()
    st.toast(f'{name.lower()} deleted')
    time.sleep(2)
    st.rerun()

def remove_multiple_users(names: list):
    for name in names:
        ref_cont = db.reference(f"/content_container/usernames/{name}")
        ref_cred = db.reference(f"/credentials/usernames/{name}")
        ref_cont.delete()
        ref_cred.delete()
        st.toast(f'{name.lower()} deleted')
    time.sleep(2)
    st.rerun()


# --- GET DB CONTENT---
def get_content():
    user_content = db.reference(f"/content_container").get() # load user content
    return user_content


# --- CONTENT BELOW DIDN'T WORK. CAUSED AN ERROR IN STREAMLIT.
# SETTING THE KEY VALUE MAKES THE CODE NOT LOAD... TO BE TESTED LATER
#for user, content in user_content.get("usernames").items():
    #vejledning = content.get("vejledning")
    #st.header(user)
    #st.text(f"Vejledningstid: {vejledning}")
    #st.write(user_content["usernames"])



#users = user_content.get('usernames')
#for user in users:

    #st.header(user)
    #problemformulering_vejledning = users.get(user).get("vejledning")

    #vejledninger = users.get(user).get("vejledning")
    #if vejledninger != None:
        #vejledning_1 = datetime.strptime(vejledninger[0], '%Y-%m-%d %H:%M:%S')
        #st.caption(f'Vejledningstid: {vejledning_1}')

    #st.write(users.get(user))
    #users.get(user).get("content")
    #st.subheader("Underemne")
    #st.write(users.get(user).get("content").get("underemne"))
    #st.subheader("Gruppekontrakt")
    #st.write(users.get(user).get("content").get("gruppekontrakt"))
    #st.subheader("Problemformulering")
    #st.write(users.get(user).get("content").get("problemformulering"))
