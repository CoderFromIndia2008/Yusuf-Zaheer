import streamlit as st
import pandas as pd
import home
import core

base_dir = core.base_dir
data_dir = core.data_dir

years = [year.name for year in data_dir.iterdir() if year.is_dir()]
years.sort(reverse=True)
full_months = core.full_months
key = False

def display(register, year):
    mismatch, modified_register = core.deleted(register, year)
    
    if mismatch and st.button("**Show deleted?**"):
        return modified_register
        
    return register

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

    register_path = data_dir / f"{year}/{month}.csv"
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
    
    year = col1.selectbox("Select year:", years, key="101")
    current_month = core.get_current_month(year)
    month = col2.selectbox("Select month:", full_months, index=current_month, key="102")
    st.divider()
    date = st.slider("Want to specify date?", min_value=0, max_value=38, step=1)
    
    if year and month:
        output = core.view(date, month, year)
        st.write(display(output, year))
    
elif page == options[3]:
    col1, col2, col3 = st.columns(3)
    
    year = col1.selectbox("Select year:", years, key="103")
    current_month = core.get_current_month(year)
    month1 = col2.selectbox("Select month:", full_months, index=current_month, key="104")
    idx = full_months.index(month1)
    month2 = col3.selectbox("Select month:", full_months[idx:], key="105")
    st.divider()
    
    if year and month1 and month2:
        working_days, output = core.percent(month1, month2, year)
        
        if working_days != 0:
            st.write(f"Total working days: {working_days}")
        
        st.write(display(output, year))
        
elif page == options[4]:
    user_input = st.text_input(
        "Enter password:",
        help="If no password is set yet, your input below will become the password"
        )

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
    year = st.selectbox("Select year:", years, key="106")
    meta_path = data_dir / str(year) / "metadata.csv"
    metadata = pd.read_csv(meta_path)
    
    metadata = display(metadata, year)
    st.divider()
    modified_metadata = st.data_editor(metadata)
        
    if st.button("**Make changes?**"):
        modified_metadata.to_csv(meta_path, index=False)
        st.success("Changes made!")

elif key and option == options[1]:
    col1, col2 = st.columns(2)
    
    year = col1.selectbox("Select year:", years, key="107")
    month = col2.selectbox("Select month:", full_months, key="108")
    
    if year and month:
        register_path = data_dir / f"{year}/{month}.csv"
        register = pd.read_csv(register_path)
        register = display(register, year)
        st.divider()
        modified_register = st.data_editor(register)
        
        if st.button("**Make changes?**"):
            modified_register.to_csv(register_path, index=False)
            st.success("Changes made!")
    
elif key and option == options[2]:
    pass
    
elif key and option == options[3]:
    year = st.selectbox("Select year:", years, key="109")
    meta_path = data_dir / str(year) / "metadata.csv"
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