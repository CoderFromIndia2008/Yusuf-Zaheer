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
key=utils.GetKey(), 
) 

month = utils.SelectMonth("Month", session)
    
with st.expander(":material/discover_tune: More filters"):
    date = utils.SelectDate(month)
        
st.divider()
register = core.ViewRegister(date, month, session)

if date != 0:
    st.caption(f"Attendance for {date}-{month}, {session}")

else:
    st.caption(f"Attendance for {month}, {session}")

utils.Display(register, session)

