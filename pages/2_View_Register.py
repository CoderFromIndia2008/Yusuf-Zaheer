import streamlit as st
import utils
import core

utils.title(
"View Register", 
"table",
"View attendance register of any session, any month and any date."
)

utils.MakeState("date", int(utils.date))
utils.MakeState("month", utils.month)
utils.MakeState("session", utils.sessions[0] if utils.sessions != [] else None)

col1, col2 = st.columns(2)

st.session_state["session"] = col1.selectbox(
"Academic session", 
utils.sessions, 
index=None, 
key="1"
) or st.session_state["session"]

st.session_state["month"] = col2.selectbox(
"Month", 
utils.full_months, 
index=None,
key="2",
) or st.session_state["month"]

with st.expander("More filters"):
    default = 0
    if st.session_state["session"] == st.GetSession().name:
        default = st.session_state["date"]
        
    st.session_state["date"] = st.number_input(
    "Choose a date (0 = whole month)", 
    min_value=0, 
    max_value=31, 
    step=1,
    value=default,
    key="3"
    ) 

st.divider()

register = core.ViewRegister(
st.session_state["date"], 
st.session_state["month"],
st.session_state["session"]
)

utils.Display(register, st.session_state["session"])

