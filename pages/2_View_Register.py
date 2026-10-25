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
key="1"
) 

month = col2.selectbox(
"Month", 
utils.full_months, 
index=utils.cur_month_idx,
key="2",
)

with st.expander("More filters"):
    date = st.number_input(
    "Choose a date (0 = whole month)", 
    min_value=0, 
    max_value=31, 
    step=1,
    value=int(utils.date),
    key="3"
    ) 

st.divider()

register = core.ViewRegister(date, month, year)

utils.Display(register, session)

