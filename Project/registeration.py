import streamlit as st
import pathlib as pt
import random as rn
import pandas as pd
import preprocessor
import core
import csv
import cv2

def camera_capture(name, camera_index):        
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
    #cv2.destroyAllWindows()

def upload_videos(name, num):
    video = st.file_uploader("Upload a video: ", type=["mp4", "mov", "webm"], key=f"{num}file_upload")

    if video:
        with open(core.tools_dir / "collection_target.mp4", "wb") as f:
            f.write(video.getbuffer())
    
        camera_capture(name, core.tool_dir / "collection_target.mp4")
        

def register_student():
    st.divider()
    name = st.text_input("Enter student name: ", key="1000").strip()
    roll = st.slider(
        "Enter student roll number: ", 
        min_value=1,
        max_value=38,
        step=1,
        key="1001"
    )
    st.header("Upload three videos for registration:")
    st.subheader("Instructions:")
    st.write("""
    - Two videos should be indoors with different colour backgrounds.
    - One video should be outside with sky or trees in the background.
    - Make sure your whole face remains clearly visible throughout the video.
    - Make the video dynamic, move your face around, show different emotions, walk from one place to another, etc.
    """)        

    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        upload_videos(name, 1)
    with col2:
         upload_videos(name, 2)
    with col3:
        upload_videos(name, 3)

    _, month, year = core.get_time()

    if month in ["Jan", "Feb", "Mar"]:
        year += 1
    session = f"20{year}-{year+1}"
    session_dir = core.data_dir / session
    meta_path = core.get_meta_path(session)

    if not meta_path.exists():
        session_dir.mkdir(exist_ok=True)
        metadata = pd.DataFrame(columns=["roll", "name"])
        metadata.loc[0] = (roll, name)
        metadata.to_csv(meta_path, index=False)
        st.success("Registration Successful!")
        return None
    
    metadata = pd.read_csv(meta_path)
    records = []
    for i in range(metadata.shape[0]):
        _roll, _name = metadata.iloc[i]
        records.append((_roll, _name))

    records.append((roll, name))
    records.sort()

    if st.button("**Register**"):
        st.divider()

        with open(meta_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["roll", "name"])
            writer.writerows(records)

        st.success("Registration Successful!")

        show = pd.read_csv(meta_path)
        st.write(show)