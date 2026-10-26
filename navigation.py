import streamlit as st 
import dummy_data
import utils

pages_dir = utils.base_dir / "app_pages"

st.logo(":material/familiar_face_and_zone:", size="large")

pages = [
st.Page(pages_dir / "0_Home.py", title="Homepage", icon=":material/home:"),
st.Page(pages_dir / "1_Mark_Attendance.py", title="Mark Attendance", icon=":material/photo_camera:"),
st.Page(pages_dir / "2_View_Register.py", title="View Register", icon=":material/table:"),
st.Page(pages_dir / "3_Attendance_Percent.py", title="Attendance Percent", icon=":material/percent:"),
st.Page(pages_dir / "4_Student_Profile.py", title="Student Profile", icon=":material/school:"),
st.Page(pages_dir / "5_Modify.py", title="Make Changes", icon=":material/manufacturing:"),
]

page = st.navigation(pages, position="top")
page.run()