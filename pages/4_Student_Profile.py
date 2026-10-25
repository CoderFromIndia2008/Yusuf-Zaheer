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
    session = st.selectbox("Session", utils.GetSession().name, key="222")

metadata, path = utils.GetFile(session, type="meta")
if metadata is None:
    st.error("No attendance available.")

names = list(metadata["name"])

with col2: 
    name = st.selectbox("Select student", names, index=None, key="333")

st.divider()
register, working_days = core.AttendancePercent("April", "March", session)

if register is None:
    st.error("No attendance available.")

else:
    utils.subheader("Attendance overview", "history_edu", "Summary of this student's attendance.")

    idx = list(register["name"] == name).index(True)
    percent = register.loc[idx, "%"]
    total = register.loc[idx, "Total"]

    col1, col2, col3 = st.columns(3)

    register, path = core.AttendancePercent(utils.month, utils.month, session)
    if register is None:
        this_month = 0
    else:
        this_month = register.loc[idx, "Total"]

    with col1: utils.metric("Present this month", this_month, "green")

    with col2: utils.metric("Total attendance", total, "blue")

    with col3: utils.metric("Present %", percent, "gray")

    st.divider()
