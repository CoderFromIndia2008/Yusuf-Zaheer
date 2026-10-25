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
    session = st.selectbox("Session", utils.sessions, key="222")

metadata, path = utils.GetFile(session, type="meta")
if metadata is None:
    st.error("No students registered.")

names = list(metadata["name"])

with col2: 
    name = st.selectbox("Select student", names, key="333")

st.divider()
full_register, total_working_days = core.AttendancePercent("April", "March", session)

if full_register is None:
    st.error("No attendance available.")

else:
    utils.subheader("Attendance overview", "history_edu", "Summary of this student's attendance.", divider=False)

    idx = list(full_register["name"] == name).index(True)
    percent = full_register.loc[idx, "%"]
    total = full_register.loc[idx, "Total"]

    col1, col2, col3 = st.columns(3, border=True)

    month_register, month_working_days = core.AttendancePercent(utils.month, utils.month, session)
    if month_register is None:
        this_month = 0
    else:
        this_month = month_register.loc[idx, "Total"]

    with col1: utils.metric("Present this month", f"{this_month}/{month_working_days}", "green")

    with col2: utils.metric("Total attendance", f"{total}/{total_working_days}", "blue")

    with col3: utils.metric("Present %", percent, "gray")

    st.divider()

utils.subheader("Attendance trends", "bar_chart", "Observe the increase and decrease in attendance throughout the year.", divider=False)

month_wise = core.MonthWiseRegister(idx, session)

st.bar_chart(month_wise, x_label="Months", y_label="Attendance")