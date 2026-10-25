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

session = col1.selectbox(
"Academic session", 
utils.sessions, 
key="4",
) 

from_month = col2.selectbox(
"From month", 
utils.full_months, 
key="5",
index=utils.cur_month_idx, 
)

idx = utils.full_months.index(from_month)
to_month = col3.selectbox(
"To month", 
utils.full_months[idx:], 
key="6"
)
    
register, working_days = core.AttendancePercent(from_month, to_month, session)

st.metric("Total working days", working_days)
utils.Display(register, session)
    
    