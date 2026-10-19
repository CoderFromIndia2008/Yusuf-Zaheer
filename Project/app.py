import streamlit as st
import pathlib as pt
import pandas as pd
import backbone
import time

options = [
    "Home",
    "Mark Attendance",
    "View Attendance",
    "Total Attendance",
    "Make Changes",
    "Remove Student",
]
    
st.title(":violet[AI ATTENDANCE SYSTEM]")
st.divider()

day, date, cmonth, cyear = time.strftime("%A %d %B %Y").split()
    
st.sidebar.write(
f"""It's **{day}**,
{date} {cmonth} {cyear}"""
)
months = backbone.full_months
cmonth = backbone.full_months.index(cmonth)

st.sidebar.divider()
page = st.sidebar.radio("", options)

dbpath = pt.Path("/workspaces/Yusuf-Zaheer/database")
metapath = dbpath / "metadata.csv"
register = pd.read_csv(metapath)

years = [year.name for year in dbpath.iterdir() if year.is_dir()]
years.sort(reverse=True)

if page == options[0]: #home
    import home

elif page == options[1]: #mark attendance
    img = st.camera_input("Take a photo: ")

    if img:
        st.success("Capture successful!")
        student, confidence, register = backbone.mark(img, model="model2")
        st.write("Student:", student)
        st.write(f"Confidence: {confidence}%")
        st.divider()
        st.table(register)
            
elif page == options[2]: #view attendance register
    col1, col2 = st.columns(2)
    
    with col1:
        year = st.selectbox("Select a year:", years)
    
    with col2:
        month = st.selectbox("Select a month:", months, index=cmonth)
        date = st.slider("Specify a date:", min_value=0, max_value=31, step=1)
        st.caption("Zero for entire month")

    register = backbone.view(month, year, str(date))
        
    full_names = tuple(pd.read_csv(metapath)["name"])
    if len(full_names) != register.shape[0] and st.button("**Show deleted?**"):
        register = backbone.show_deleted(register)
            
    st.dataframe(register)

elif page == options[3]: #view attendance total and percentage    
    year = st.selectbox("Select a year:", years)
    col1, col2 = st.columns(2)
    
    with col1:
        start_month = st.selectbox("Select starting month:", months, key="month1", index=cmonth)

    with col2:
        start = months.index(start_month)
        stop_month = st.selectbox("Select ending month:", months[start:], key="month2", index=cmonth)
        stop = months.index(stop_month) + 1

    selected_months = months[start:stop]
    working_days, register = backbone.percent(selected_months, year)
        
    full_names = tuple(pd.read_csv(metapath)["name"])
    if len(full_names) != register.shape[0] and st.button("**Show deleted?**"):
        register = backbone.show_deleted(register, full_names)
        
    st.caption("Working days:", working_days)
    st.dataframe(register)

elif page == options[4]: #make changes to a register
    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox("Select a year:", years)

    with col2:
        month = st.selectbox("Select a month:", months, index=cmonth)

    path = dbpath / f"{year}/{month}.csv"
    
    if not path.exists():
        st.error(f"No records available for {month} {year}")
        
    register = pd.read_csv(path)
        
    full_names = tuple(pd.read_csv(metapath)["name"])
    if len(full_names) != register.shape[0] and st.button("**Show deleted?**"):
        register = backbone.show_deleted(register)
        
    editable_df = st.data_editor(register)

    if st.button("**Make Changes?**"):
        editable_df.to_csv(path, index=False)
        st.success("Register changed!")

elif page == options[5]: #remove a student
    register = pd.read_csv(metapath)    

    selection = []
    for idx, name in enumerate(register["name"]):
        selection.append(f"{idx+1}. {name}")
        
    if len(selection) == 0:
        st.error("No students registered")
    
    name = st.selectbox("Select a student:", selection, index=None)
    
    if name and st.button("**:red[DELETE]**"):
        backbone.remove(name, selection)


