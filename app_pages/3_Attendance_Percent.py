import streamlit as st
import utils
import core

utils.title(
"Attendance Percent", 
"percent",
"Review total attendance across a selected month range."
)

col1, col2, col3 = st.columns([1.2, 1, 1])

session = col1.selectbox(
"Academic session", 
utils.sessions, 
key=utils.GetKey(),
) 

with col2:
    from_month = utils.SelectMonth("From month", session, utils.full_months)

idx = utils.full_months.index(from_month)
with col3:
    to_month = utils.SelectMonth("To month", session, utils.full_months[idx:])
    
register, working_days = core.AttendancePercent(from_month, to_month, session)
st.metric("Total working days", working_days)
st.caption("Click on a column header to order by ascending or descending.")
utils.Display(register, session)