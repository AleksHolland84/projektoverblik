import streamlit as st
import nivo_chart as nc   
import time
from datetime import date, datetime, time as t
from pathlib import Path
import firebase_admin
from firebase_admin import db, credentials
import yaml
from yaml.loader import SafeLoader
from db_module import *
from auth_module import *
import pandas as pd
import json
from io import BytesIO
import streamlit_authenticator as stauth # pip install streamlit-authenticator

### NOTES TO MY SELF - I NEED TO USE THE CALLBACK FUNCTION WHEN TEXTING IN THE TEXT_AREA AREA. 
### I THINK THIS WILL HELP WHIT THE RACE CONDITION - SOMETIMES THE THE APP DOESN'T UPLOAD THE DATA TO THE DB.
### I THINK THIS IW BECAUSE, THE APP RERUNS ONCE THE USER PRESSES OUTSIDE THE TEXT AREA. THIS WILL THEN RERUN 
### BEFORE THE APP UPLOADS THE CONTET TO THE DB


#-- GLOBAL VARIABLES ---
current_date = date.today().strftime("%Y-%m-%d")
version = "1.0"

# -- DB AUTHENTICATION
db_creds = dict(st.secrets['firebase']['db_access'])
@st.cache_resource # cache the initializing of the db
def load_db():
    cred = credentials.Certificate(db_creds)
    return firebase_admin.initialize_app(cred, {"databaseURL":st.secrets['firebase']['url']})


# Setup config - to configure title of webpage
st.set_page_config(page_title='Projekt overblik', page_icon="🧪",)
st.caption(f"version {version}")
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
if authentication_status and username == "admin":
    # --- ADMIN ACCESS ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Velkommen {name}")
    from admin_module import *

    app_users = get_content()
    if app_users.get("usernames') != None:
        list_of_users = [user for user in app_users.get('usernames')]
    else:
        list_of_users = list()
    #st.write(list_of_users) # write list of users

    # --- ADD NEW USER ---
    st.header('Tilføj ny gruppe')
    with st.form(key="admin_add_user"):
        new_user = st.text_input('Navn:', value=None, max_chars=20)
        password_new_user = st.text_input("Password", max_chars=20)
        st.caption('Husk at sætte password!')
        if st.form_submit_button('Tilføj gruppe'):
            if add_user(name = new_user, users= list_of_users):
                if create_user_login(new_user, [password_new_user]):
                    st.rerun()

    # --- SHOW USER CONTENT ---
    st.header('Vis gruppens afleverede indhold')
    selected_user = st.selectbox("Vis indhold",
              list_of_users)
    user_data = app_users.get('usernames').get(selected_user)
    st.subheader(selected_user)

    buffer = BytesIO()

    json_data = json.dumps(user_data) #
    st.json(json_data) # display json data in app
    buffer.write(json_data.encode()) # write encoded json string to buffer
    st.download_button(f'Download data', buffer.getvalue(), file_name=f'{selected_user}_projektoverblik_{current_date}.json')


    # --- REMOVE USER---
    st.subheader('Delete grupper/bruger')
    col1, col2 = st.columns(2)
    with col2:
        confirm = st.checkbox(f'Delete {selected_user}?')
    with col1:
        if st.button(f'Delete {selected_user}'):
            if confirm:
                remove_user(name = selected_user)
            else:
                st.toast("Check 'Delete gruppe' for at delete valgte gruppe")
                time.sleep(2)

    options = st.multiselect('Delete grupper', list_of_users)
    if st.button('Delete grupper!'):
        remove_multiple_users(names = options)

if authentication_status and username != "admin":
    # --- USER ACCESS
    # --- SIDEBAR ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Velkommen {name}")

    with st.sidebar:

        with open('Projektplan.pdf', 'rb') as projektplan:
            st.download_button(label='Download Projetkplan',
                               data=projektplan,
                               file_name='Projektplan.pdf',
                               mime='application/octet-stream')


    # --- DISPLAY CONTENT IN APP---
    # Load user and content from DB
    user_content = db.reference(f"/content_container/usernames/{username}/content/").get() # load user content
    logbook = db.reference(f"/content_container/usernames/{username}/").get() # load user logbook
    emner = db.reference("/content_container/emne/Fremtidens samfund").get() # load underemner
    vejledninger = db.reference(f"/content_container/usernames/{username}/vejledning/").get()




    # --- TITLE ---
    st.title("Projekt overblik")

    # --- DISPLAY INTRO AND WARNING ---
    st.markdown('''
                Et værktøj til at skabe overblik og hjælpe med at opfylde de forskellige krav
                under projekt ugen i folkeskolen. Når I uploader, gemmes tekstfeltets data i en database.

                :red[Upload ikke personfølsom data!]

                ''')

    st.header("Uge 2", divider = "grey")
    # --- UNDEREMNER ---
    # generate a list of subtopics in the selectbox
    underemner_list = [underemne for underemne in emner.get("underemner")]

    # --- display selectbox with underemner
    pre_sel = db.reference(f"/content_container/usernames/{username}/content/underemne").get()
    if pre_sel is not None:
        # get index of previous underemne
        selbox_index = underemner_list.index(pre_sel)
    else:
        selbox_index = None

    _underemne = st.selectbox(
        "Valg af delemne",
        underemner_list, index=selbox_index)
    if _underemne != pre_sel:
        ref = db.reference(f"/content_container/usernames/{username}/content")
        ref.update({"underemne": _underemne})
        st.toast("Opdaterer underemne")
        time.sleep(2)


    st.header("Uge 3", divider = "grey")
    if text_area(label="Gruppekontrakt", value=user_content.get('gruppekontrakt'), ref=f"/content_container/usernames/{username}/content", toast="Gruppekontrakt uploaded!"):
        add_contribution(username=username, value=1, date = datetime.now().strftime("%Y-%m-%d")) # add contribution to graph
        st.rerun()
    if text_area(label="Undersøgelsesspørgsmål", value=user_content.get('undersøgelsesspørgsmål'), ref=f"/content_container/usernames/{username}/content", toast="Undersøgelsesspørgsmål uploaded!"):
        add_contribution(username=username, value=1, date = datetime.now().strftime("%Y-%m-%d")) # add contribution to graph
        st.rerun()
    if text_area(label="Problemformulering", value=user_content.get('problemformulering'), ref=f"/content_container/usernames/{username}/content", toast="Problemformulering uploaded!"):
        add_contribution(username=username, value=1, date = datetime.now().strftime("%Y-%m-%d")) # add contribution to graph
        st.rerun()
        

    # --- SET VEJLEDNINGSTID ---
    col1, col2, col3 = st.columns(3)
    with col1:
        if vejledninger != None:
            vejledning_1 = datetime.strptime(vejledninger[0], '%Y-%m-%d %H:%M:%S').date()
            st.caption(f'Vejledningstid: {vejledning_1}')
        else:
            vejledning_1 = "today"
            st.caption(f'Vejledningsdato: Ingen aftalt dato')
        problemformulering_vejledningsdato = st.date_input(label="Vejlednings dato", value=vejledning_1)


    with col2:
        if vejledninger != None:
            vejledning_1_tid = datetime.strptime(vejledninger[0], '%Y-%m-%d %H:%M:%S').time()
            st.caption(f'Vejledningstid: {vejledning_1_tid}')
        else:
            vejledning_1_tid = t(hour = 12, minute = 00)
            st.caption(f'Vejledningstid: Ingen aftalt dato')

        problemformulering_vejledningstid = st.time_input(label="Vejledning tid", value=vejledning_1_tid)

    with col3:
        pass


    st.header("Uge 4", divider = "grey")
    # --- GENERATE TEXT AREA FOR EACH DAY IN WEEK 4 ---
    week_day_list = ['mandag', 'tirdag', 'onsdag', 'torsdag', 'fredag']
    for day in week_day_list:
        st.subheader(day.capitalize())
        logbog = logbook.get('logbog')
        date = log_book(username = username, label=f"Logbog for {day}", value=logbog.get(f'logbog for {day}'), ref=f"/content_container/usernames/{username}/logbog", toast=f"Logbog for {day} uploaded!")
        if date:
            pass
            #print(date)

    # --- CREATE BUFFER AND DOWNLOAD BUTTON ---
    buffer = BytesIO()
    json_user_data = json.dumps(db.reference(f"/content_container/usernames/{username}").get()) # serialize dumped db content
    buffer.write(json_user_data.encode()) # write encoded json string to buffer
    st.download_button(f'Download data', buffer.getvalue(), file_name=f'{username}_projektoverblik_{current_date}.json')

    # --- CONTRIBUTION GRAPH DATA --
    data = db.reference(f"/content_container/usernames/{username}/graph/data").get()
    lst_data = [{"day": key, "value" : value} for key, value in data.items()] # generate a list of dictionaries of data, eg. [{"day": "2023-12-12", "value": 5}, {"day": "2023-12-13", "value": 10}]


    from streamlit_javascript import st_javascript
    st_theme = st_javascript("""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")""")
    if st_theme == "dark":
        BorderColor = "#1e1f1e"
        BoxColor = "#303030"
    else:
        BorderColor= "#ffffff"
        BoxColor = "#eeeeee"


    # GUIDE https://github.com/aswan-heart-centre/streamlit_nivo
    if data is not None:
        contribution_graph = {
            "data":
                lst_data,
            "layout": {
                "title": "Aktivitetskalender",
                "type": "calendar",
                "height": 300,
                #"width": 700,
                "from": "2023-01-15",
                "to": "2024-01-26",
                "emptyColor": BoxColor,
                "colors": ["#bfe8bc", "#8de887", "#0fc402", "#084704"],
                "margin": {"top": 20, "right": 20, "bottom": 20, "left": 20},
                "yearSpacing": 40,
                "monthBorderColor": BorderColor,
                "dayBorderWidth": 2,
                "dayBorderColor": BorderColor,
                "legends": [
                    {
                        "anchor": "bottom-right",
                        "direction": "row",
                        "translateY": 36,
                        "itemCount": 4,
                        "itemWidth": 42,
                        "itemHeight": 36,
                        "itemsSpacing": 14,
                        "itemDirection": "right-to-left",
                    }
                ],
            },
        }
        nc.nivo_chart(data=contribution_graph["data"], layout=contribution_graph["layout"],key="calendar_chart")

    st.stop()

    # --- FOTTER ---
