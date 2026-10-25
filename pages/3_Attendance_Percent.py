import streamlit as st
import utils
import core

utils.title(
"Attendance Percent", 
"percent",
"Review total attendance across a selected month range. \
Click on a column header to order by ascending or descending."
)

col1, col2, col3 = st.columns([1.2, 1, 1])

st.session_state["session"] = col1.selectbox(
"Academic session", 
utils.sessions, 
key="103",
index=None
) or st.session_state["session"]

utils.MakeState("from")
if st.sessions["from"] is not None:
    idx = utils.full_months.index(st.session_state["from"])
else:
    idx = utils.cur_month_idx
    
st.session_state["from"] = col2.selectbox(
"From month", 
utils.full_months, 
key="104",
index=idx, 
)

idx = utils.full_months.index(st.session_state["from"])
st.session_state["to"] = col3.selectbox(
"To month", 
utils.full_months[idx:], 
key="105"
)
    
register, working_days = core.AttendancePercent(
st.session_state["from"],
st.session_state["to"],
st.session_state["session"]
)

st.metric("Total working days", working_days)
utils.Display(register, st.session_state["session"])
    
    