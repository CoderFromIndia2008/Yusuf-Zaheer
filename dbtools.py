import streamlit as st
import random as rn
import pandas as pd
import pickle
import utils
import csv
import cv2

#Turn videos ro frame, preprocess them and save to dataset for model training.
def VideoToDataset(Name, camera_index):        
    capture = cv2.VideoCapture(camera_index)
    count = 0
    
    while True:
        success, frame = capture.read()
        count += 1
        if not success:
            break
        rotate = rn.choices([True, False], [35, 65])[0]
        processed_img = utils.ProcessImage(frame, rotate=rotate)
        split = rn.choices(['Train', 'Test', 'Evaluate'], [75, 20, 5])[0]
        folder = utils.tools_dir / "dataset" / split / Name
        folder.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(folder / f"{count}.png", processed_img)
    capture.release()

#Display last 5 change log and download complete change log file
def changeLog():
    utils.subheader(
    "Change log",
    "history",
    "Log history of actions like changing student name, attendance. \
    The download button is below.",
    divider=False
    )

    path = utils.tools_dir / "change_log.dat"
    path.touch(exist_ok=True)
    records, txt_file = [], ""
    file = open(path, "rb")
    
    while True:
        try:
            record = pickle.load(file)
            records.append(record)
            txt_file += ";".join(record) + "\n"
            
        except:
            break
        
    records.reverse()

    num, max_value, default = 5, len(records), 5
    if len(records) < 5:
        max_value, default = len(records), len(records)

    with st.expander(":material/discover_tune: More filters"):
        num = st.number_input(
        "Number of records shown", 
        min_value=0, 
        max_value=max_value, 
        step=1, 
        value=default,
        key="2020"
        )

    with st.container(border=True):
        if records == []:
            st.write("No changes yet.")
            return None
            
        for record in records[:num]:
            text = utils.pretty(record[0][1:], "gray", True, "schedule")
            text += "\n\n"
            
            if len(record) > 2:
                text += utils.pretty(record[1], "gray", True) + "\n\n"

                for change in record[2:]:
                    text += utils.pretty(change, "green", True) + "\n\n"
                    
                st.info(text)
                st.divider()

    st.download_button(
    "Download change log",
    txt_file,
    file_name="change_log.txt",
    icon=":material/download:",
    width="stretch"
    )

#add new change log
def writeLog(changes):
    record = [f"- {utils.hour}:{utils.minute} {utils.date}-{utils.month[:3]}-{utils.year}"]
    
    record.extend(changes)
    with open(utils.tools_dir / "change_log.dat", "ab") as file:
        pickle.dump(record, file)

#upload a video
def Upload(Name, num):
    video = st.file_uploader(
    "Upload a video", 
    type=["mp4", "mov", "webm"], 
    key=f"{num}file_upload"
    )
    
    if not video:
        return None
    img_path = utils.tools_dir / "etc/collection_target.mp4"
    with open(img_path, "wb") as file:
        file.write(video.getbuffer())
    VideoToDataset(Name, img_path)

def data_editor(original, key):
    cols = original.columns
    original = original.set_index("Roll")
    modified = st.data_editor(original, height="content", key=key)
    modified = modified.reset_index()
    modified.columns = cols
    return modified
    
#change name of a student in a given session. 
def ModifyName():
    utils.subheader(
    "Modify Student Details",
    "person_edit",
    "Change name of one or more students in the table below.",
    )
    
    session = st.selectbox("Academic session", utils.sessions, key="10")
    metadata, path = utils.getFile(session, type="meta")
    if metadata is None:
        st.error("No students registered yet.")
        return None

    modified = data_editor(metadata, key="change name")
    not_modified = modified.equals(metadata)

    if st.button("**Make changes**", width="stretch", type="primary", disabled=not_modified):
        modified.to_csv(path, index=False)
        st.success("Changes made!")
    else:
        return None

    truth_table = []
    change_log = ["Changed name(s)", f"Session: {session}"]

    for idx in metadata.index:
        mismatch = metadata.loc[idx, "Name"] != modified.loc[idx, "Name"]
        truth_table.append(mismatch)

        if mismatch:
            change_log.append(f"{metadata.loc[idx, 'Name']} \
            (Roll No. {metadata.loc[idx, 'Roll']}) -> \
            {modified.loc[idx, 'Name']}")

    for month in utils.full_months:
        register, path = utils.getFile(month, session, type="register")

        if register is None:
            continue

        for idx, is_changed in enumerate(truth_table):
            if is_changed:
                register.loc[idx, "Name"] = modified.loc[idx, "Name"]

        register.to_csv(path, index=False)

    writeLog(change_log)

#change attendance from present to absent and vice versa in any register
def ModifyRegister():
    utils.subheader(
    "Modify Attendance",
    "edit_document",
    "Change attendance of one or more students in the table below.",
    )
    
    col1, col2 = st.columns(2)
    session = col1.selectbox("Academic session", utils.sessions, key="11")
    month = col2.selectbox(
    "Month", 
    utils.full_months, 
    index=utils.cur_month_idx, 
    key="12"
    )

    register, path = utils.getFile(month, session, type="register")
    if register is None:
        st.error("No register available for this month.")
        return None

    modified = data_editor(register, "change register")
    not_modified = modified.equals(register)

    if st.button("**Make changes**", width="stretch", key="Name button", type="primary", disabled=not_modified):
        modified.to_csv(path, index=False)
        st.success("Changes made!")

        change_log = [f"Changed register", f"Month: {month} | Session: {session}"]
        for idx_row in register.index:
            for idx_col, mark in enumerate(register.iloc[idx_row, 2:]):
                if mark != modified.iloc[idx_row, idx_col+2]:
                    change_log.append(f"{register.loc[idx_row, 'Name']} \
                    (Roll No. {register.loc[idx_row, 'Roll']}) \
                    for date {idx_col+1}: {mark} -> \
                    {modified.iloc[idx_row, idx_col+2]}")

        writeLog(change_log)
    
#add a new student to the current session metadata file
def RegisterStudent():
    utils.subheader(
    "Register Student",
    "person_add",
    "Add a new student to the session.",
    )
    Name = st.text_input("Student name", value=None, key="14")
    Roll = st.number_input(
    "Student roll number", 
    min_value=0,
    max_value=38,
    step=1,
    key="15",
    value=None
    )
    st.divider()
    utils.subheader(
    "Instructions",
    "help",
    "Upload three videos for model training (face recognition).",
    divider=False
    )
    st.write("""
    - Two videos should be indoors with different colour backgrounds.
    - One video should be outside with sky or trees in the background.
    - Make sure your whole face remains clearly visible throughout the video.
    - Make the video dynamic, move your face around, show different emotions, walk from one place to another, etc.
    """)
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1: Upload(Name, 1)
        with col2: Upload(Name, 2)
        with col3: Upload(Name, 3) 
    metadata, path = utils.getFile(type="meta")
    consent = st.button("**Register**", width="stretch", key="register student", disabled=not(Name and Roll), type="primary")
    if consent and metadata is None:
        utils.getSession().mkdir(exist_ok=True)
        metadata = pd.DataFrame(columns=["Roll", "Name"])
        metadata.loc[0] = (Roll, Name)
        metadata.to_csv(path, index=False)
        st.success("Registration Successful!")
        
        change_log = ["Created session + Registered student", f"Name: {Name} | Roll: {Roll}"]
        writeLog(change_log)
        return None  

    if consent and Name in tuple(metadata["Name"]):
        st.error("Name already registered.")
        return None 
    elif consent and Roll in tuple(metadata["Roll"]):
        st.error("Roll number already exists.")
        return None
    metadata.loc[metadata.shape[0]] = (Roll, Name)
    metadata = metadata.sort_values("Roll")   
    if consent:
        metadata.to_csv(path, index=False)            
        st.success("Registration Successful!")
        change_log = ["Registered student", f"Name: {Name} | Roll No. {Roll}"]
        writeLog(change_log)
    
#remove a student from the current session's metadata file
def RemoveStudent():
    utils.subheader(
    "Remove Student",
    "delete",
    "Remove a student from the register. Previous attendance is not deleted.",
    )
    metadata, path = utils.getFile(type="meta")
    if metadata is None:
        st.error("No students registered.")
        return None   
    options, Names = [], list(metadata["Name"])
    for idx, Name in enumerate(metadata["Name"]):
        options.append(f"{idx+1}. {Name}")
    if len(options) == 0:
        st.error("No students registered.")
        return None     
    option = st.selectbox(
    "Select a student", 
    options, 
    key="16", 
    index=None
    )
    st.divider()     
    if option:
        idx = options.index(option)
        Name = Names[idx]
        metadata = metadata.drop(idx, axis=0)    
    if option and st.toggle("Sort Roll numbers", value=True):
        metadata.iloc[idx:, 0] -= 1
    st.caption("Your changes will appear in the table below.")
    utils.pagination(metadata.set_index("Roll"), "df", "1001")
    if st.button("**Remove Student**", width="stretch", key="2003", type="primary", disabled=option is None):
        metadata.to_csv(path, index=False)
        st.success("Student removed.")
        change_log = [
        "Removed student", 
        f"Name: {Name} | Roll No. {idx+1}"
        ]
        writeLog(change_log)