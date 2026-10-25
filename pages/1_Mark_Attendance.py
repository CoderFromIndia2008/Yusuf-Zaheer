import streamlit as st
import utils
import core

st.set_page_config("Mark Attendance", page_icon=":material/:photo_camera"),

utils.title(
"Mark Attendance", 
"photo_camera",
"Just take a photo and the attendance will be marked automatically."
)

with st.container(border=True):
    st.write("**Before taking the photo**")
    st.markdown("""
    - Ensure that face is clearly visible in the camera.
    - The lighting is good and camera remains steady.
    - Avoid other faces appearing in the photo.
    """)
    
    img = st.camera_input("Take a photo")
    model = st.file_uploader("Upload a model", type=["keras"])
    
if img:
    st.success("Capture successful!")
    student, confidence, register = core.MarkAttendance(img, model)
    if register:
        st.success("Prediction successful!")
        st.write("Student:", student)
        st.write(f"Confidence: {confidence:.1f}%")
        st.divider()
        st.write(register.set_index("roll"))
            
