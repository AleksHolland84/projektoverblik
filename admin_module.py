# --- MODULES FOR ADMIN PANEL ---
import streamlit as st
import streamlit_authenticator as stauth
from firebase_admin import db, credentials
import time
from datetime import datetime, time as t
import json
import pandas as pd


# --- ADD USER TO DB ---
def add_user(name: str, users: list, password: list, cls: str):
    if "admin" in name:
        st.error('Navne der indeholder "admin", er ikke tilladt!')
        return False
    if name in users:
        st.warning(f'{name} findes allerede')
        return False
    if create_user_login(name, password, cls):
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

def create_user_login(name: str, password: list, cls: str):
    hashed_pass = stauth.Hasher(password).generate()
    ref = db.reference(f"/credentials/usernames")
    if name.lower() in ref.get():
        print("User exists")
        return False
    else:
        print("creating new user in db")
        login_template = {
            name.lower() : {
                "name": name.lower(),
                "password": hashed_pass[0],
                "role": "elev",
                "class": cls,
                }
            }
        ref.update(login_template)
        return True
        

# --- ADD TEACHER TO DB ---
def add_teacher(name: str, users: list, password: list, cls_list: list):
    name = name.lower()
    if "admin" in name:
        st.error('Navne der indeholder "admin", er ikke tilladt!')
        return False
    if name in users:
        st.warning(f'{name} findes allerede')
        return False
    if create_teacher_login(name, password, cls_list):
        ref = db.reference(f"/teachers/usernames")
        user_template = {
            name.lower() :{
                "classes": cls_list
                }
            }
        ref.update(user_template)
        st.toast(f'{name.lower()} added')
        time.sleep(2)
        return True
    
def edit_teacher(name: str, classes: list):
    try:
        ref = db.reference(f"/teachers/usernames/{name}/")
        template = {"classes": classes}
        ref.update(template)
        for cls in classes:
            st.toast(f'Classes: {cls} added to {name.lower()}')
    except  Exception as e:
        print(e)
        print("Error at edit_teacher")


def create_teacher_login(name: str, password: list, cls_list: list):
    hashed_pass = stauth.Hasher(password).generate()
    ref = db.reference(f"/credentials/usernames")
    if name.lower() in ref.get():
        print("Teacher exists")
        return False
    else:
        print("creating new user in db")
        login_template = {
            name.lower() : {
                "name": name.lower(),
                "password": hashed_pass[0],
                "role": "lærer",
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

def get_class(cls: str):
    user_creds = db.reference(f"/credentials").get() # load user content
    cls_list = [user for user in user_creds.get('usernames') if user_creds.get('usernames').get(user).get("class") == cls]
    return cls_list

def get_teachers():
    teacher_creds = db.reference(f"/teachers").get() # load user content
    cls_list = [teacher for teacher in teacher_creds.get("usernames")]
    return cls_list
