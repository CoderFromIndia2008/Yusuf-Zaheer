import streamlit as st
import utils
import core

utils.title(
"Student Profile", 
"school",
"Review a student's attendance throughout the session."
)

col1, col2 = st.columns(2)

with col1:
    session = st.selectbox("Session", utils.GetSession, key="222")

metadata, path = utils.GetFile(type="meta")
if metadata is None:
    st.error("No attendance available.")

names = list(metadata["name"])

with col2: 
    name = st.selectbox("Select student", names, index=None, key="333")

register, working_days = core.AttendancePercent("April", utils.cur_month_idx, session)
if register is None:
    st.error("No attendance available.")

else:
    utils.subheader("Attendance overview", "history_edu", "")

    roll = (register["name"] == name).index(True) + 1
    percent = register.loc[roll-1, "%"]

    col1, col2, col3 = st.columns(3)

    with col1: utils.metric("Present this month", name, "green")

    with col2: utils.metric("Total attendance", roll, "blue")

    with col3: utils.metric("Present %", percent, "gray")

    st.divider()
