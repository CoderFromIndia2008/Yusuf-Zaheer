import streamlit as st
import pandas as pd
import home
import core

base_dir = core.base_dir
data_dir = core.data_dir

sessions = [session.name for session in data_dir.iterdir() if session.is_dir()]
sessions.sort(reverse=True, key=lambda x: int(x[-2:]))
full_months = core.full_months
key = False

def display(register, year):
    mismatch, modified_register = core.deleted(register, year)
    if mismatch and st.toggle("**Show deleted**"): 
        return register.set_index("roll")
        
    return modified_register.set_index("roll")

options = [
    "**:material/Home: Home**",
    "**:material/photo_camera: Mark Student**",
    "**:material/table: View Register**",
    "**:material/percent: Percentage**",
    "**:material/table_edit: Modify**",
]

st.title(":violet[**AI ATTENDANCE SYSTEM**]")
st.divider()

side = st.sidebar
page = side.radio("**Select an option:**", options, key="100")

if page == options[0]:
    date, month, year = core.get_time()
    session_dir = core.get_session_dir(year)
    register_path = core.get_register_path(session_dir.name, month)

    if register_path.exists():
        register = pd.read_csv(register_path)

        if str(date) in register.columns:
            total_strength = register.shape[0]
            present = sum(register[str(date)] == "P")
            absent = sum(register[str(date)] == "A")

            col1, col2, col3 = st.columns(3, border=True, wrap=False)
            col1.metric(":green[**Present Today**]", value=f"{present}/{total_strength}")  
            col2.metric(":red[**Absent Today**]", value=f"{absent}/{total_strength}")
            col3.metric(":gray[**Present** :material/percent:]", value=f"{present / total_strength * 100 :.1f}%")
            st.divider()

    else:
        pass

    home.home()
    
elif page == options[1]:
    img = st.camera_input(
        "Take a photo:",
        help="Make sure your face is clearly visible and no other faces appear in the photo."
        )
    
    if img:
        st.success("Capture successful!")
        student, confidence, register = core.mark(img, model="model1")
        st.write("Student:", student)
        st.write(f"Confidence: {confidence}%")
        st.divider()
        st.write(register)
    
elif page == options[2]:
    col1, col2 = st.columns(2)
    session = col1.selectbox("Select session:", sessions, key="101")
    current_month = core.get_current_month(session)
    month = col2.selectbox("Select month:", full_months, index=current_month, key="102")
    st.divider()
    date = st.slider("Want to specify date?", min_value=0, max_value=31, step=1)
    
    if session and month:
        output = core.view(date, month, session)
        if type(output) == str:
            st.write(output)
        else:
            st.write(display(output, session))
    
elif page == options[3]:
    col1, col2, col3 = st.columns(3)
    session = col1.selectbox("Select session:", sessions, key="103")
    current_month = core.get_current_month(session)
    month1 = col2.selectbox("Select month:", full_months, index=current_month, key="104")
    idx = full_months.index(month1)
    month2 = col3.selectbox("Select month:", full_months[idx:], key="105")
    st.divider()
    
    if session and month1 and month2:
        working_days, output = core.percent(month1, month2, session)
        if working_days != 0:
            st.write(f"Total working days: {working_days}")
        
        st.write(display(output, session))
        
elif page == options[4]:
    user_input = st.text_input(
        "Enter password:",
        help="If no password is in place yet, your input below will become the password"
        );st.caption("Password is 123")

    if user_input:
        key = core.password(user_input)
    
        if key == False:
            st.write("Incorrect Password")

options = [
    "**Modify name/roll**",
    "**Modify register**",
    "**Register student**",
    "**Remove student**"
]

if key:
    option = st.sidebar.radio("**Additional options:**", options)

if key and option == options[0]:
    session = st.selectbox("Select session:", sessions, key="106")
    meta_path = core.get_meta_path(session)
    metadata = pd.read_csv(meta_path)
    metadata = display(metadata, session)
    st.divider()
    modified_metadata = st.data_editor(metadata, num_rows="dynamic")
        
    if st.button("**Make changes?**"):
        modified_metadata.to_csv(meta_path, index=False)
        st.success("Changes made!")

elif key and option == options[1]:
    col1, col2 = st.columns(2)
    session = col1.selectbox("Select session:", sessions, key="107")
    month = col2.selectbox("Select month:", full_months, key="108")
    
    if session and month:
        register_path = core.get_register_path(session, month)
        register = pd.read_csv(register_path)
        register = display(register, session)
        st.divider()
        modified_register = st.data_editor(register)
        
        if st.button("**Make changes?**"):
            modified_register.to_csv(register_path, index=False)
            st.success("Changes made!")
    
elif key and option == options[2]:
    st.subheader(":red[Sorry!]")
    st.write("This page is still work in progress...")
    
elif key and option == options[3]:
    session = st.selectbox("Select session:", sessions, key="109")
    meta_path = core.get_meta_path(session)
    metadata = pd.read_csv(meta_path)    
    options = []

    for idx, name in enumerate(metadata["name"]):
        options.append(f"{idx+1}. {name}")
        
    if len(options) != 0:
        name = st.selectbox("Select a student:", options, key="110")
        if name and st.button("**Make Changes?**"):
            st.write(core.remove(name, options))
        
    else:
        st.write("No students registered")