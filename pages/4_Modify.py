import streamlit as st
import dbtools
import utils

utils.title(
"Make Changes", 
"manufacturing",
"Change attendance records and student details."
)

utils.MakeState("key", False)

options = [
"**Change Log**",
"**Modify Name**",
"**Modify Register**",
"**Register Student**",
"**Remove Student**"
]

if st.session_state["key"] == False:
    utils.Password()

elif st.button("Close modification page", icon=":material/lock:"):
    st.session_state["key"] = False

else:
    tabs = st.tabs(options)
    
    with tabs[0]: 
        dbtools.ChangeLog()

    with tabs[1]: 
        dbtools.ModifyName()

    with tabs[2]:
        dbtools.ModifyRegister()

    with tabs[3]: 
        dbtools.RegisterStudent()

    with tabs[4]: 
        dbtools.RemoveStudent()
    