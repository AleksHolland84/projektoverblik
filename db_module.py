# --- MODULES FOR DB AND STREAMLIT---
import streamlit as st
from firebase_admin import db, credentials
import time
from datetime import datetime

# --- Generate streamlit text_area
def text_area(username: str, label: str, value: str, ref: str, toast: str):
    _input = st.text_area(label = label, value=value)
    if st.button(f"Upload {label}"):
        ref = db.reference(ref)
        ref.update({label.lower(): _input})
        st.toast(toast)
        add_contribution(username=username, value=1) # add contribution to graph
        time.sleep(2)
        #st.rerun()
        return True

# --- Function displau st.text_area. If db contains text, the text_area's
# --- label will contain the db content. Also, it db contains text,
# --- the date for uploading text is displayed ---
def log_book(username: str, label: str, value: str, ref: str, toast: str):
    if value != None:
        _input = st.text_area(label = label, value=value[0])
    else:
        _input = st.text_area(label = label, value=value)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Upload {label}"):
            ref = db.reference(ref)
            ref.update({label.lower():{
                0:_input,
                1: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }})
            st.toast(toast)
            time.sleep(2)
            add_contribution(username = username, value: int = 1)
           # st.rerun()
    if value:
        if len(value) > 1:
            with col2:
                if value[1] != "":
                    st.write(f'Uploaded: {value[1]}')
            return value[1] # return date of upload

# --- Function to add value to the contribution graph ---
def add_contribution(username: str, value: int = 1):
    ref = db.reference(f"/content_container/usernames/{username}/graph/data/")
    data = ref.get()
    date = datetime.now().strftime("%Y-%m-%d")
    value_of_contribution = data.get(date)
    if value_of_contribution:
        ref.update({date: value_of_contribution + value})
    else:
        ref.update({date: value})
