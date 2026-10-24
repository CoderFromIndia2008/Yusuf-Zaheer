import streamlit as st
import random as rn
import pandas as pd
import preprocessor
import pickle
import core
import csv
import cv2

sessions = core.GetSessionList()
full_months = core.full_months
              
def CameraCapture(name, camera_index):        
    capture = cv2.VideoCapture(camera_index)
    count = 0
    while True:
        success, frame = capture.read()
        count += 1
        if not success:
            st.write("Could not read from camera")
            break
        rotate = rn.choice([True, False])
        processed_img = preprocessor.process(frame, rotate=rotate)
        split = rn.choices(['Train', 'Test', 'Evaluate'], [75, 20, 5])[0]
        folder = core.tools_dir / "Dataset" / split / name
        folder.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(folder / f"{count}.png", processed_img)
    capture.release()

def change_log():
    st.subheader(":blue[:material/history: Change log]")
    st.caption("Brief log history of actions like changing student name, attendance. For complete history, click the download button below.")
    log_path = core.tools_dir / "change_log.dat"
    log_path.touch(exist_ok=True)
    records = []
    file = open(log_path, "rb")
    while True:
        try: records.append(pickle.load(file))
        except: break
    records.reverse()        
    with st.container(border=True):
        if records == []:
            st.write("No changes yet.")
            return None
        for record in records[:5]:
            st.write(f"**:gray[:material/schedule: {record[0][1:]}]**")
            if len(record)>2:
                st.write(f"**:green[{record[1]}]**")
                for change in record[2:]:
                    st.caption(f"**:green-background[{change}]**")
                st.divider()

    txt = []
    for record in records:
        txt.append(";".join(record))
    txt = "\n".join(txt)
    st.download_button(
    ":material/download: Download change log",
    txt,
    width="stretch"
    )

def write_change_log(changes):
    record = [f"- {core.hour}:{core.minute} {core.date}-{core.month[:3]}-20{core.year}"]
    record.extend(changes)
    with open(core.tools_dir / "change_log.dat", "ab") as file:
        pickle.dump(record, file)

def upload_videos(name, num):
    video = st.file_uploader(
    "Upload a video", 
    type=["mp4", "mov", "webm"], 
    key=f"{num}file_upload"
    )
    if not video:
        return None
    img_path = core.tools_dir / "collection_target.mp4"
    file = open(img_path, "wb")
    file.write(video.getbuffer())
    file.close()
    CameraCapture(name, img_path)
    
def modify_name():
    st.subheader(":blue[:material/person_edit: Modify Student Details]")
    st.caption("Change name of one or more students in the table below.")
    st.write("")
    session = st.selectbox("Academic session", sessions, key="106")
    meta_path = core.GetMetaPath(session)
    metadata = pd.read_csv(meta_path)
    st.write("")
    modified = st.data_editor(metadata, column_order=("name",), hide_index=True)
    
    if not (metadata.equals(modified)) and st.button("**Make changes**", width="stretch", type="primary"):
        modified.to_csv(meta_path, index=False)
        st.success("Changes made!")
    else:
        return None

    truth = []
    changes = ["Changed name(s)", f"session: {session}"]
    for idx in metadata.index:
        mismatch = metadata.loc[idx, "name"] != modified.loc[idx, "name"]
        truth.append(mismatch)
        if mismatch:
            changes.append(f"{metadata.loc[idx, 'name']} (roll: {metadata.loc[idx, 'roll']}) -> {modified.loc[idx, 'name']}")
    for month in full_months:
        register_path = core.GetRegisterPath(session, month)
        if not register_path.exists():
            continue
        register = pd.read_csv(register_path)
        for idx, changed in enumerate(truth):
            if changed:
                register.loc[idx, "name"] = modified.loc[idx, "name"]
        register.to_csv(register_path, index=False)
    write_change_log(changes)
    
def modify_register():
    st.subheader(":blue[:material/edit_document: Modify Attendance]")
    st.caption("Change attendance of one or more students in the table below.")
    col1, col2 = st.columns(2)
    session = col1.selectbox("Academic session", sessions, key="107")
    current_month = core.GetCurrentMonth(session)
    month = col2.selectbox("Month", full_months, index=current_month, key="108")
    if not (session and month):
        return None
        
    register_path = core.GetRegisterPath(session, month)
    if not register_path.exists():
        st.error("No register available for this month.")
        return None
    register = pd.read_csv(register_path)
    st.write("")
    modified = st.data_editor(register, hide_index=True)
          
    if (not register.equals(modified)) and st.button("**Make changes**", width="stretch", key="2001", type="primary"):
        modified.to_csv(register_path, index=False)
        st.success("Changes made!")
        changes = [f"Changed register", f"month: {month} | session: {session}"]
        for idx_row in register.index:
            for idx_col, mark in enumerate(register.iloc[idx_row, 2:]):
                if mark != modified.iloc[idx_row, idx_col+2]:
                    change = f"{register.loc[idx_row, 'name']} (roll: {register.loc[idx_row, 'roll']}) for date {idx_col+1}: {mark} -> {modified.iloc[idx_row, idx_col+2]}"
                    changes.append(change)
        write_change_log(changes)
    
def register_student():
    st.subheader(":blue[:material/person_add: Register Student]")
    st.caption("Add a new student to the session.")
    name = st.text_input("Student name", key="1000").strip()
    roll = st.number_input(
    "Student roll number", 
    min_value=0,
    max_value=38,
    step=1,
    key="1001"
    )
    st.divider()
    st.subheader(":blue[:material/help: Instructions]")
    st.caption("Upload three videos for model training (face recognition).")
    st.write("""
    - Two videos should be indoors with different colour backgrounds.
    - One video should be outside with sky or trees in the background.
    - Make sure your whole face remains clearly visible throughout the video.
    - Make the video dynamic, move your face around, show different emotions, walk from one place to another, etc.
    """)
    st.write("")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1: upload_videos(name, 1)
        with col2: upload_videos(name, 2)
        with col3: upload_videos(name, 3)
    month, year = core.month, core.year
    if month in ["Jan", "Feb", "Mar"]:
        year += 1
    session = f"20{year}-{year+1}"
    session_dir = core.data_dir / session
    meta_path = core.GetMetaPath(session)
  
    if (not meta_path.exists()) and st.button("**Register**", width="stretch", key="2002", type="primary"):
        session_dir.mkdir(exist_ok=True)
        metadata = pd.DataFrame(columns=["roll", "name"])
        metadata.loc[0] = (roll, name)
        metadata.to_csv(meta_path, index=False)
        st.success("Registration Successful!")
        change = ["Registered student", f"name: {name} | roll: {roll}"]
        write_change_log(change)
        return None
    elif not meta_path.exists():
        return None
      
    metadata = pd.read_csv(meta_path)
    if name in list(metadata["name"]):
        st.error("Name already registered")
        return None
    elif roll in list(metadata["roll"]):
        st.error("Roll number already exists")
        return None
    records = []
    for i in range(metadata.shape[0]):
        _roll, _name = metadata.iloc[i]
        records.append((_roll, _name))
    records.append((roll, name))
    records.sort()
  
    if name and roll and st.button("**Register**", width="stretch", key="2002", type="primary"):
        with open(meta_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
            writer.writerows(records)
        st.success("Registration Successful!")
        change = ["Registered student", f"name: {name} | roll: {roll}"]
        write_change_log(change)
        metadata = pd.read_csv(meta_path)
    
def remove_student():
    st.subheader(":blue[:material/delete: Remove Student]")
    st.caption("Remove a student from the register. Previous attendance is not deleted.")
    session = core.GetSession(core.year, core.month)
    meta_path = core.GetMetaPath(session)
    if not meta_path.exists():
        st.error("No students registered")
        return None
    metadata = pd.read_csv(meta_path)    
    options, names = [], []
    for idx, name in enumerate(metadata["name"]):
        options.append(f"{idx+1}. {name}")
        names.append(name)
    if len(options) == 0:
        st.error("No students registered")
        return None
    else:
        option = st.selectbox("Select a student", options, key="110", index=None)
        st.divider()
        if option and st.button("**Remove Student**", width="stretch", key="2003", type="primary"):
            idx = options.index(option)
            name = names[idx]
            st.success("Student removed")
            core.RemoveStudent(idx)
            change = ["Removed student", f"name: {name} | roll: {idx+1}"]
            write_change_log(change)

def modify():
    options = [
    "**Change Log**",
    "**Modify Name**",
    "**Modify Register**",
    "**Register Student**",
    "**Remove Student**"
    ]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(options)
    with tab1: change_log()
    with tab2: modify_name()
    with tab3: modify_register()
    with tab4: register_student()
    with tab5: remove_student()
    
        