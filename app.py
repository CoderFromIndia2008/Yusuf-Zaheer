import streamlit as st
import modification
import home
import core

base_dir = core.base_dir
data_dir = core.data_dir
full_months = core.full_months
sessions = core.GetSessionList()

def DisplayAdjusted(original, session):
    if original is None:
        st.error("No attendance available")
        return None
    mismatch, modified = core.AdjustNames(register, session)
    if mismatch and st.toggle("Display removed student(s)"): 
        st.write(register.set_index("roll"))
        return None
    st.write(modified.set_index("roll"))

options = [
    "**:material/Home: Home**",
    "**:material/photo_camera: Mark Student**",
    "**:material/table: View Register**",
    "**:material/percent: Percentage**",
    "**:material/manufacturing: Modify**",
]

st.sidebar.title(":violet[**:material/familiar_face_and_zone: AI Attendance**]")
st.sidebar.caption("Attendance Marking and Management System with AI")
st.sidebar.divider()
page = st.sidebar.radio(":violet[**Pages**]", options, key="100")
st.sidebar.divider()

#PAGE 1: HOME
if page == options[0]:
    st.title(":violet[:material/home: Home]")
    st.caption("Summary of today's attendance and learn about the project.")
    st.divider()
    st.subheader(":blue[:material/today: Today's overview]")
    date, month, year = core.date, core.month, core.year
    st.caption(f"Attendance for {date} {month} 20{year}")
    session = core.GetSession(year, month)
    register = core.ViewRegister(date, month, session)
    if register is None or str(date) not in register.columns:
        st.info(f"No Attendance marked for {date} {month} 20{year}")

    else:
        total_strength = register.shape[0]
        present = sum(register[str(date)] == "P")
        absent = sum(register[str(date)] == "A")
        col1, col2, col3 = st.columns(3, border=True)
        col1.metric(":green[**Present Today**]", value=f"{present}/{total_strength}")  
        col2.metric(":red[**Absent Today**]", value=f"{absent}/{total_strength}")
        col3.metric(":gray[**Present** :material/percent:]", value=f"{present / total_strength * 100 :.1f}%")
        st.divider()
        st.subheader(":blue[:material/table: Today's register]")
        DisplayAdjusted(register, session)
        st.divider()

    home.home()
    home.ascii()

#PAGE 2: MARK ATTENDANCE
elif page == options[1]:
    st.title(":violet[:material/photo_camera: Mark Attendance]")
    st.caption("Just take a photo and the attendance will be marked automatically.")
    st.divider()
    st.warning("TEMPORARILY DISABLED")
    with st.container(border=True):
        st.write("**Before taking the photo**")
        st.markdown("""
        - Ensure that face is clearly visible in the camera.
        - The lighting is good and camera remains steady.
        - Avoid other faces appearing in the photo.
        """)
        img = st.camera_input("Take a photo")
    
    if img:
        st.success("Capture successful!")
    if img and st.button("**Predict & Mark Attendance**", width="stretch"):
        student, confidence, register = core.MarkAttendance(img, model_name="China")

        if not student:
            st.error("No student detected!")
        else: 
            st.success("Prediction successful!")
            st.write("Student:", student)
            st.write(f"Confidence: {confidence}%")
            st.divider()
            st.write(register)
    
#PAGE 3: VIEW ATTENDANCE REGISTER
elif page == options[2]:
    st.title(":violet[:material/table: View Register]")
    st.caption("View attendance register of any session, any month and any date.")
    st.divider()
    col1, col2 = st.columns(2)
    session = col1.selectbox("Academic session", sessions, key="101")
    current_month = core.GetCurrentMonth(session)
    month = col2.selectbox("Month", full_months, index=current_month, key="102")
    with st.expander("More filters"):
        date = st.number_input(
        "Choose a date (0 = whole month)", 
        min_value=0, 
        max_value=31, 
        step=1)

    if session and month:
        st.write("");st.write("")
        register = core.ViewRegister(date, month, session)
        DisplayAdjusted(register, session)

#PAGE 4: VIEW ATTENDANCE PERCENTAGE
elif page == options[3]:
    st.title(":violet[:material/percent: Attendance Percent]")
    st.caption("Review total attendance across a selected month range. Click on a column header to order by ascending or descending.")
    st.divider()
    col1, col2, col3 = st.columns([1.2, 1, 1])
    session = col1.selectbox("Academic session", sessions, key="103")
    current_month = core.GetCurrentMonth(session)
    from_month = col2.selectbox("From month", full_months, index=current_month, key="104")
    idx = full_months.index(from_month)
    to_month = col3.selectbox("To month", full_months[idx:], key="105")
    
    if session and from_month and to_month:
        working_days, register = core.AttendancePercent(from_month, to_month, session)
        st.metric("Total working days", working_days)
        DisplayAdjusted(register, session)

#PAGE 5: MAKE CHANGES TO DATABASE
elif page == options[4]:
    st.title(":violet[:material/manufacturing: Make Changes]")
    st.caption("Change attendance records and student details.")
    st.write("")
    if "key" not in st.session_state:
        st.session_state["key"] = False

    @st.dialog(":violet[:material/key: Authentication Required]")
    def CheckPassword():
        user_input = st.text_input("Enter password", type="password")
        st.caption(":gray[Hint: Password is 123]")

        message = core.PasswordVerify()
        if st.button(message, key="1100", width="stretch", type="primary", disabled=(not user_input)):
            st.session_state["key"] = core.PasswordVerify(user_input)
            if st.session_state["key"] == True:
                st.rerun()
            else:
                st.error("Incorrect Password")

    if st.session_state["key"] == False:
        CheckPassword()

    if st.button(":material/lock: Close modification page"):
        st.session_state["key"] = False

    if st.session_state["key"] == True:
        modification.modify()