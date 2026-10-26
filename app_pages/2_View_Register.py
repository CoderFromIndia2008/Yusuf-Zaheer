import streamlit as st
import utils
import core

utils.title(
"View Register", 
"table",
"View attendance register of any session, any month and any date."
)

session = utils.GetSession().name
month, date = utils.cur_month_idx, utils.date
def reset():
    global month, session
    if session != utils.GetSession().name:
        month = "April"
        date = 0

    if month != utils.month:
        date = 0

col1, col2 = st.columns(2)
session = col1.selectbox("Academic session", utils.sessions, key="1", on_change=reset()) 

month = col2.selectbox(
"Month", 
utils.full_months, 
index=None,
key="2",
on_change=reset()
) or month

if month == utils.month and session == utils.GetSession().name:
    default =int(utils.date)
else:
    default = 0


with st.expander(":material/discover_tune: More filters"):
    date = st.number_input(
    "Choose a date (0 = whole month)", 
    min_value=0, 
    max_value=31, 
    step=1,
    value=None,
    key="3"
    ) or date

st.divider()
register = core.ViewRegister(date, month, session)
utils.Display(register, session)

