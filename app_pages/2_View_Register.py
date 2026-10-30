import streamlit as st
import utils
import core

utils.title(
"View Register", 
"table",
"View attendance register of any session, any month and any date."
)
col1, col2 = st.columns(2)
session = col1.selectbox(
"Academic session",
utils.sessions, 
key="session input 1", 
) 

with col2:
    if session == utils.getSession().name:
        month = utils.selectMonth("Month", "month input 1")
    else:
        month = utils.selectMonth("Month", "month input 2", default=0) 
with st.expander(":material/discover_tune: More filters"):
    if month == utils.month:
        date = utils.selectDate("date input 1")
    else:
        date = utils.selectDate("date input 2", 0)
        
st.divider()
register = core.viewRegister(date, month, session)
if date != 0:
    st.caption(f"Attendance for {date}-{month}, {session}")
else:
    st.caption(f"Attendance for {month}, {session}")
utils.display(register, session)

