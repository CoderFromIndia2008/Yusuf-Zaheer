import streamlit as st
import dbtools
import utils

utils.title(
"Make Changes", 
"manufacturing",
"Change attendance records and student details."
)

options = [
"**Change Log**",
"**Modify Name**",
"**Modify Register**",
"**Register Student**",
"**Remove Student**"
]

if st.session_state["key"] == False:
    utils.Password()

if st.button(":material/lock: Close modification page"):
    st.session_state["key"] = False

if st.session_state["key"] == True:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(options)
    
    with tab1: dbtools.ChangeLog()
    with tab2: dbtools.ModifyName()
    with tab3: dbtools.ModifyRegister()
    with tab4: dbtools.RegisterStudent()
    with tab5: dbtools.RemoveStudent()
    