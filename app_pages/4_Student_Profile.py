import matplotlib.pyplot as plt
import streamlit as st
import utils
import core

utils.title(
"Student Profile", 
"school",
"Review a student's attendance throughout the session."
)

col1, col2 = st.columns(2)

session = col1.selectbox("Session", utils.sessions, key="7")

metadata, path = utils.GetFile(session, type="meta")
if metadata is None:
    st.error("No students registered.")
    st.stop()

options, names = [], []
for idx, name in enumerate(metadata["name"]):
    options.append(f"{idx+1}. {name}")
    names.append(name)

with col2: 
    option = st.selectbox("Select student", options, key="8")
    idx = options.index(option)
    name = names[idx]

st.divider()
full_register, total_working_days = core.AttendancePercent("April", "March", session)

if full_register is None:
    st.error("No attendance available.")
    st.stop()

utils.subheader(
"Attendance overview", 
"history_edu", 
"Summary of this student's attendance.", 
divider=False
)

idx = list(full_register["name"] == name).index(True)
percent = full_register.loc[idx, "%"]
total = full_register.loc[idx, "Total"]
this_month_register, month_working_days = core.AttendancePercent(utils.month, utils.month, session)
    
if this_month_register is None:
    month_attendance = 0
else:
    month_attendance = this_month_register.loc[idx, "Total"]

if session == utils.GetSession().name:
    col0, col1, col2 = st.columns(3, border=True)
    with col0: 
        utils.metric("Present this month", f"{month_attendance}/{month_working_days}", "green")
else:
    col1, col2 = st.columns(2, border=True)

with col1: 
    utils.metric("Total attendance", f"{total}/{total_working_days}", "blue")
with col2: 
    utils.metric("Total Present %", percent, "gray")

st.divider()
utils.subheader(
"Attendance trends", 
"bar_chart", 
"Observe the increase and decrease in attendance throughout the year.", 
divider=False
)
st.write("")

df = core.MonthWiseRegister(idx, session)
fig, ax = plt.subplots()
bars = ax.bar(df["month"], df["total"], color=df["colour"], label=df["label"])

ax.set_facecolor("none")
plt.ylim(0, 31)
plt.bar_label(bars, label_type="center", color="#525e75")
plt.legend(loc="lower right", fancybox=True, framealpha=0.5)
plt.tight_layout()

st.pyplot(fig, transparent=True)
