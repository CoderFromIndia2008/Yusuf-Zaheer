import streamlit as st
import utils
import core

utils.title(
"View Register", 
"table",
"View attendance register of any session, any month and any date."
)

col1, col2 = st.columns(2)

session = col1.selectbox("Academic session", utils.sessions, key="101")
st.session_state["session"] = session or st.session_state["session"]

st.session_state["month"] = col2.selectbox(
"Month", 
utils.full_months, 
index=utils.cur_month_idx,
key="102",
) or st.session_state["month"] 

with st.expander("More filters"):
    st.session_state["date"]  = st.number_input(
    "Choose a date (0 = whole month)", 
    min_value=0, 
    max_value=31, 
    step=1)

st.divider()

register = core.ViewRegister(
st.session_state["date"], 
st.session_state["month"],
st.session_state["session"]
)

utils.Display(register, session)

