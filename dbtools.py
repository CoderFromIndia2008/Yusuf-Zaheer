import streamlit as st
import random as rn
import pandas as pd
import pickle
import utils
import core
import csv
import cv2

#Turn videos ro frame, preprocess them and save to dataset for model training.
def VideoToDataset(name, camera_index):        
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
        folder = utils.tools_dir / "dataset" / split / name
        folder.mkdir(parents=True, exist_ok=True)
        
        cv2.imwrite(folder / f"{count}.png", processed_img)
        
    capture.release()

#Display last 5 change log and download complete change log file
def ChangeLog():
    utils.subheader(
    "Change log",
    "history",
    "Brief log history of actions like changing student name, attendance. \
    For complete history, click the download button below.",
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

    num = 5
    with st.expander(":material/discover_tune: More filters"):
        num = st.number_input(
        "Number of records shown", 
        min_value=0, 
        max_value=len(records), 
        step=1, 
        value=5,
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
def WriteLog(changes):
    record = [f"- {utils.hour}:{utils.minute} {utils.date}- \
    {utils.month[:3]}-20{utils.year}"]
    
    record.extend(changes)
    with open(utils.tools_dir / "change_log.dat", "ab") as file:
        pickle.dump(record, file)

#upload a video
def Upload(name, num):
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
        
    VideoToDataset(name, img_path)
    
#change name of a student in a given session. 
def ModifyName():
    utils.subheader(
    "Modify Student Details",
    "person_edit",
    "Change name of one or more students in the table below.",
    )
    
    session = st.selectbox("Academic session", utils.sessions, key="106")
    
    metadata, path = utils.GetFile(session, type="meta")
    
    if metadata is None:
        st.error("No students registered yet.")
        return None
    
    modified = st.data_editor(metadata, column_order=["name"], hide_index=True)
    is_modified = not metadata.equals(modified)
    
    if is_modified and st.button("**Make changes**", width="stretch", type="primary"):
        modified.to_csv(path, index=False)
        st.success("Changes made!")
        
    else:
        return None

    truth_table = []
    change_log = ["Changed name(s)", f"Session: {session}"]
    
    for idx in metadata.index:
        mismatch = metadata.loc[idx, "name"] != modified.loc[idx, "name"]
        truth_table.append(mismatch)
        
        if mismatch:
            change_log.append(f"{metadata.loc[idx, 'name']} \
            (Roll No. {metadata.loc[idx, 'roll']}) -> \
            {modified.loc[idx, 'name']}")
            
    for month in utils.full_months:
        register, path = utils.GetFile(month, session, type="register")
        
        if register is None:
            continue
            
        for idx, is_changed in enumerate(truth_table):
            if is_changed:
                register.loc[idx, "name"] = modified.loc[idx, "name"]
                
        register.to_csv(path, index=False)
        
    WriteLog(change_log)

#change attendance from present to absent and vice versa in any register
def ModifyRegister():
    utils.subheader(
    "Modify Attendance",
    "edit_document",
    "Change attendance of one or more students in the table below.",
    )
    
    col1, col2 = st.columns(2)
    
    session = col1.selectbox("Academic session", utils.sessions, key="107")
    
    month = col2.selectbox(
    "Month", 
    utils.full_months, 
    index=utils.cur_month_idx, 
    key="108"
    )

    register, path = utils.GetFile(month, session, type="register")
    
    if register is None:
        st.error("No register available for this month.")
        return None
        
    modified = st.data_editor(register, hide_index=True)
    is_modified = not register.equals(modified)
    
    if is_modified and st.button("**Make changes**", width="stretch", key="2001", type="primary"):
        modified.to_csv(path, index=False)
        st.success("Changes made!")
        change_log = [f"Changed register", f"Month: {month} | Session: {session}"]
        
        for idx_row in register.index:
            for idx_col, mark in enumerate(register.iloc[idx_row, 2:]):
                if mark != modified.iloc[idx_row, idx_col+2]:
                    change_log.append(f"{register.loc[idx_row, 'name']} \
                    (roll: {register.loc[idx_row, 'roll']}) \
                    for date {idx_col+1}: {mark} -> \
                    {modified.iloc[idx_row, idx_col+2]}")
        
        WriteLog(change_log)
    
#add a new student to the current session metadata file
def RegisterStudent():
    utils.subheader(
    "Register Student",
    "person_add",
    "Add a new student to the session.",
    )
    
    name = st.text_input("Student name", value=None, key="1000")
    roll = st.number_input(
    "Student roll number", 
    min_value=0,
    max_value=38,
    step=1,
    key="1001",
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
        with col1: Upload(name, 1)
        with col2: Upload(name, 2)
        with col3: Upload(name, 3)
        
    metadata, path = utils.GetFile(type="meta")

    if name and roll and metadata is None and st.button("**Register**", width="stretch", key="2002", type="primary"):
        utils.GetSession().mkdir(exist_ok=True)
        
        metadata = pd.DataFrame(columns=["roll", "name"])
        metadata.loc[0] = (roll, name)
        metadata.to_csv(path, index=False)
        
        st.success("Registration Successful!")
        
        change_log = ["Created session + Registered student", f"Name: {name} | Roll: {roll}"]
        WriteLog(change_log)
        
        return None
        
    elif not (name and roll) or metadata is None :
        return None
      
    if name in tuple(metadata["name"]):
        st.error("Name already registered.")
        return None
        
    elif roll in tuple(metadata["roll"]):
        st.error("Roll number already exists.")
        return None

    metadata.loc[metadata.shape[0]] = (roll, name)
    metadata = metadata.sort_values("roll")
        
    if name and roll and st.button("**Register**", width="stretch", key="2002", type="primary"):
        metadata.to_csv(path, index=False)            
        st.success("Registration Successful!")
        
        change_log = ["Registered student", f"Name: {name} | Roll: {roll}"]
        WriteLog(change_log)
    
#remove a student from the current session's metadata file
def RemoveStudent():
    utils.subheader(
    "Remove Student",
    "delete",
    "Remove a student from the register. Previous attendance is not deleted.",
    )
    
    metadata, path = utils.GetFile(type="meta")

    if metadata is None:
        st.error("No students registered.")
        return None
        
    options, names = [], list(metadata["name"])
    for idx, name in enumerate(metadata["name"]):
        options.append(f"{idx+1}. {name}")

    if len(options) == 0:
        st.error("No students registered.")
        return None
        
    option = st.selectbox(
    "Select a student", 
    options, 
    key="110", 
    index=None
    )
    st.divider()
        
    if option:
        idx = options.index(option)
        name = names[idx]
        metadata = metadata.drop(idx, axis=0)
        
    if option and st.toggle("Sort roll numbers", value=True):
        metadata.iloc[idx:, 0] -= 1

    st.caption("Your changes will appear in the table below.")
    st.write(metadata.set_index("roll"))

    if option and st.button("**Remove Student**", width="stretch", key="2003", type="primary"):
        metadata.to_csv(path, index=False)
    
        st.success("Student removed.")
    
        change_log = [
        "Removed student", 
        f"Name: {name} | Roll: {idx+1}"
        ]
        WriteLog(change_log)