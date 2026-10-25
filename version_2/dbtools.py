import streamlit as st
import random as rn
import pandas as pd
import pickle
import utils
import core
import csv
import cv2

def CameraCapture(name, camera_index):        
    capture = cv2.VideoCapture(camera_index)
    count = 0
    
    while True:
        success, frame = capture.read()
        count += 1
        
        if not success:
            break
            
        rotate = rn.choice([True, False])
        processed_img = utils.ProcessImage(frame, rotate=rotate)
        
        split = rn.choices(['Train', 'Test', 'Evaluate'], [75, 20, 5])[0]
        folder = utils.tools_dir / "Dataset" / split / name
        folder.mkdir(parents=True, exist_ok=True)
        
        cv2.imwrite(folder / f"{count}.png", processed_img)
        
    capture.release()

def ChangeLog():
    utils.title(
    "Change log",
    "history",
    "Brief log history of actions like changing student name, attendance. \
    For complete history, click the download button below.",
    config=False
    )
    
    path = utils.tools_dir / "change_log.dat"
    path.touch(exist_ok=True)
    
    records, txt = [], ""
    file = open(path, "rb")
    
    while True:
        try:
            record = pickle.load(file)
            records.append(record)
            txt += record + "\n"
            
        except:
            break
        
    records.reverse()        
    
    with st.container(border=True):
        if records == []:
            st.write("No changes yet.")
            return None
            
        for record in records[:5]:
            text = utils.pretty(record[0][1:], "gray", True, "schedule")
            text += "\n"
            
            if len(record) > 2:
                text += utils.pretty(record[1], "gray", True)

                for change in record[2:]:
                    text += utils.pretty(change, "green", True)
                    
                st.info(text)
                st.divider()

    st.download_button(
    ":material/download: Download change log",
    txt,
    width="stretch"
    )

def WriteLog(changes):
    record = [f"- {utils.hour}:{utils.minute} {utils.date}- \
    {utils.month[:3]}-20{utils.year}"]
    
    record.extend(changes)
    with open(utils.tools_dir / "change_log.dat", "ab") as file:
        pickle.dump(record, file)

def Upload(name, num):
    video = st.file_uploader(
    "Upload a video", 
    type=["mp4", "mov", "webm"], 
    key=f"{num}file_upload"
    )
    
    if not video:
        return None
        
    img_path = utils.tools_dir / "collection_target.mp4"
    
    with open(img_path, "wb") as file:
        file.write(video.getbuffer())
        
    CameraCapture(name, img_path)
    
def ModifyName():
    utils.title(
    "Modify Student Details",
    "person_edit",
    "Change name of one or more students in the table below.",
    config=False
    )
    
    session = st.selectbox("Academic session", utils.sessions, key="106")
    st.session_state["month"] = session or st.session_state["session"]
    
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
    
def ModifyRegister():
    utils.title(
    "Modify Attendance",
    "edit_document",
    "Change attendance of one or more students in the table below.",
    config=False
    )
    
    col1, col2 = st.columns(2)
    
    session = col1.selectbox("Academic session", utils.sessions, key="107")
    st.session_state["month"] = session or st.session_state["session"]
    
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
    
def RegisterStudent():
    utils.title(
    "Register Student",
    "person_add",
    "Add a new student to the session.",
    config=False
    )
    
    name = st.text_input("Student name", key="1000").strip()
    roll = st.number_input(
    "Student roll number", 
    min_value=0,
    max_value=38,
    step=1,
    key="1001"
    )
    
    st.divider()
    utils.title(
    "Instructions",
    "help",
    "Upload three videos for model training (face recognition)."
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
  
    if metadata is not None and st.button("**Register**", width="stretch", key="2002", type="primary"):
        utils.GetSession().mkdir(exist_ok=True)
        
        metadata = pd.DataFrame(columns=["roll", "name"])
        metadata.loc[0] = (roll, name)
        metadata.to_csv(path, index=False)
        
        st.success("Registration Successful!")
        
        change_log = ["Registered student", f"name: {name} | roll: {roll}"]
        WriteLog(change_log)
        
        return None
        
    elif metadata is None:
        return None
      
    if name in tuple(metadata["name"]):
        st.error("Name already registered")
        return None
        
    elif roll in tuple(metadata["roll"]):
        st.error("Roll number already exists")
        return None
        
    records = []
    for i in range(metadata.shape[0]):
        _roll, _name = metadata.iloc[i]
        records.append((_roll, _name))
        
    records.append((roll, name))
    records.sort()
  
    if name and roll and st.button("**Register**", width="stretch", key="2002", type="primary"):
        with open(path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
            writer.writerows(records)
            
        st.success("Registration Successful!")
        
        change_log = ["Registered student", f"name: {name} | roll: {roll}"]
        WriteLog(change_log)
    
def RemoveStudent():
    utils.title(
    "Remove Student",
    "delete",
    "Remove a student from the register. Previous attendance is not deleted.",
    config=False
    )
    
    metadata, path = utils.GetFile(type="meta")
    
    if metadata is None:
        st.error("No students registered")
        return None
        
    options, names = [], []
    for idx, name in enumerate(metadata["name"]):
        options.append(f"{idx+1}. {name}")
        names.append(name)
        
    if len(options) == 0:
        st.error("No students registered")
        return None
        
    option = st.selectbox(
    "Select a student", 
    options, 
    key="110", 
    index=None
    )
    st.divider()
        
    if option and st.button("**Remove Student**", width="stretch", key="2003", type="primary"):
        idx = options.index(option)
        name = names[idx]
        
        metadata = metadata.drop(idx, axis=0)
        metadata.iloc[idx:, 0] -= 1
        metadata.to_csv(path, index=False)
    
        st.success("Student removed")
    
        change_log = [
        "Removed student", 
        f"Name: {name} | Roll No.: {idx+1}"
        ]
        WriteLog(change_log)