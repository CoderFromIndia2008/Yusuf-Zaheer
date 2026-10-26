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
key="1", 
) 

with col2:
    if session == utils.GetSession().name:
        month = utils.SelectMonth("Month", "2")
    
    else:
        month = utils.SelectMonth("Month", "22", default=0)
    
with st.expander(":material/discover_tune: More filters"):
    if month == utils.month:
        date = utils.SelectDate("3")
    
    else:
        date = utils.SelectDate("33", 0)
        
st.divider()
register = core.ViewRegister(date, month, session)

if date != 0:
    st.caption(f"Attendance for {date}-{month}, {session}")

else:
    st.caption(f"Attendance for {month}, {session}")

utils.Display(register, session)

