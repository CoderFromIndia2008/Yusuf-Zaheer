import streamlit as st
import random as rn
import pandas as pd
import preprocessor
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
    log_path = core.tools_dir / "change_log.txt"
    log_path.touch(exist_ok=True)
    file = open(log_path)
    changes = file.readlines()
    file.close()
    log = changes
    if changes == []:
        log = ["No changes made yet."]   

    with st.container(border=True):
        for change in log[-1::-1]:
            message = change.partition(";")

            if len(message) == 3:
                details = message[2].partition(":")
                st.write(message[0])
                st.write(details[0])
                for change in details[2].split(" | "):
                    st.caption(f":green-background[{change}]")
            else:
                st.subheader(message[0])
                st.write(message[2])
    return changes

def write_change_log(change):
    report = f"- {core.hour}:{core.minute} {core.date}-{core.month[:3]}-20{core.year}; {change}\n"
    with open(core.tools_dir / "change_log.txt", "a") as file:
        file.write(report)

def upload_videos(name, num):
    video = st.file_uploader("Upload a video", type=["mp4", "mov", "webm"], key=f"{num}file_upload")
    if not video:
        return None
    file = open(core.tools_dir / "collection_target.mp4", "wb")
    file.write(video.getbuffer())
    file.close()
    CameraCapture(name, core.tool_dir / "collection_target.mp4")

def modify():
    options = [
    "**Change Log**",
    "**Modify Name/Roll**",
    "**Modify Register**",
    "**Register Student**",
    "**Remove Student**"
    ]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(options)

    with tab1:
        st.subheader(":blue[:material/history: Change log]")
        st.caption("Complete log history of actions like changing student name, attendance, registration and removal.")
        changes = change_log()

    #MODIFY NAME OR ROLL
    with tab2:
        st.subheader(":blue[:material/person_edit: Modify Student Details]")
        st.caption("Change name or roll of one or more students in the table below.")
        st.write("")
        session = st.selectbox("Academic session", sessions, key="106")
        meta_path = core.GetMetaPath(session)
        metadata = pd.read_csv(meta_path)
        st.write("")
        modified = st.data_editor(metadata, hide_index=True)
        change_register = False
        if not (metadata.equals(modified)) and st.button("**Make changes**", width="stretch", type="primary"):
            modified.to_csv(meta_path, index=False)
            st.success("Changes made!")
            change_register = True

        if change_register:
            truth = []
            full_names = tuple(modified["name"])
            for idx in metadata.index:
                truth.append(metadata.loc[idx, "name"] not in full_names)

            for month in full_months:
                register_path = core.GetRegisterPath(session, month)
                if not register_path.exists():
                    continue

                register = pd.read_csv(register_path)
                changes = []
                for idx, changed in enumerate(truth):
                    if changed:
                        changes.append(f"{register.loc[idx, 'name']} -> {modified.loc[idx, 'name']}")
                        register.loc[idx, "name"] = modified.loc[idx, "name"]

                register.to_csv(register_path, index=False)
            changes = " | ".join(changes)
            write_change_log(f"Changed name(s): {changes}")

    #MODIDY REGISTER
    with tab3:
        st.subheader(":blue[:material/edit_document: Modify Attendance]")
        st.caption("Change attendance of one or more students in the table below.")
        col1, col2 = st.columns(2)
        session = col1.selectbox("Academic session", sessions, key="107")
        current_month = core.GetCurrentMonth(session)
        month = col2.selectbox("Month", full_months, index=current_month, key="108")
        change_register = False
        if session and month:
            register_path = core.GetRegisterPath(session, month)
            register = pd.read_csv(register_path)
            st.write("")
            modified = st.data_editor(register, hide_index=True)
          
            if (not register.equals(modified)) and st.button("**Make changes**", width="stretch", key="2001", type="primary"):
                modified.to_csv(register_path, index=False)
                change_register = True
                st.success("Changes made!")

        if change_register:
            changes = []
            for idx_row in register.index:
                for idx_col, mark in enumerate(register.iloc[idx_row, 2:]):
                    if mark != modified.iloc[idx_row, idx_col+2]:
                        change = f"{register.loc[idx_row, 'name']} on {idx_col+3} {month[:3]}: {mark} -> {modified.iloc[idx_row, idx_col+2]}"
                        changes.append(change)
            changes = " | ".join(changes)
            write_change_log(f"Changed register for {month} {session}: {changes}")

    #REGISTER STUDENT
    with tab4:
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
            write_change_log(f"Registered name = {name}, roll = {roll}")
            return None
      
        metadata = pd.read_csv(meta_path)
        records = []
        for i in range(metadata.shape[0]):
            _roll, _name = metadata.iloc[i]
            records.append((_roll, _name))
  
        records.append((roll, name))
        records.sort()
  
        if name and roll and st.button("**Register**", width="stretch", key="2002", type="primary"):
            st.divider()
            with open(meta_path, "w") as file:
                writer = csv.writer(file)
                writer.writerow(["roll", "name"])
                writer.writerows(records)
            st.success("Registration Successful!")
            write_change_log(f"Registered {name}, Roll No. {roll}")
            metadata = pd.read_csv(meta_path)
            st.write(metadata)
  
    #REMOVE STUDENT
    with tab5:
        st.subheader(":blue[:material/delete: Remove Student]")
        st.caption("Remove a student from the register. Roll numbers are automatically adjusted.")
        session = st.selectbox("Academic session", sessions, key="109")
        meta_path = core.GetMetaPath(session)
        metadata = pd.read_csv(meta_path)    
        options, names = [], []

        for idx, name in enumerate(metadata["name"]):
            options.append(f"{idx+1}. {name}")
            names.append(name)
          
        if len(options) == 0:
            st.error("No students registered")
          
        else:
            option = st.selectbox("Select a student", options, key="110", index=None)
            st.divider()
            if option and st.button("**Remove Student**", width="stretch", key="2003", type="primary"):
                idx = options.index(option)
                name = names[idx]
                st.success("Student removed")
                st.write(core.RemoveStudent(idx))
                write_change_log(f"Removed {name} in {session}")

