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
key="session input 2",
) 
with st.expander(":material/discover_tune: More filters"):
    sort = st.toggle("Sort by highest attendance")
st.divider()

if session == utils.getSession().name:
    with col2:
        from_month = utils.selectMonth("From month", "5")
    with col3:
        idx = utils.full_months.index(from_month)
        to_month = utils.selectMonth("To month", "55", utils.full_months[idx:], 0)
else:
    with col2:
        from_month = utils.SelectMonth("From month", "6", utils.full_months, 0)
    with col3:
        start_idx = utils.full_months.index(from_month)
        end_idx = utils.full_months[start_idx:].index("March")
        to_month = utils.selectMonth("To month", "66", utils.full_months[start_idx:], end_idx)

register, working_days = core.attendancePercent(from_month, to_month, session)
st.metric("Total working days", working_days)

if sort:
    st.write(register.sort_values("Total", ascending=False).set_index("roll"))
else:
    utils.display(register, session)


