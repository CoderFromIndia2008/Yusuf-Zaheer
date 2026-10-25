import streamlit as st
import utils
import core

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
    
if img:
    st.success("Capture successful!")
    student, confidence, register = core.MarkAttendance(img, "model_3")
    st.success("Prediction successful!")
    st.write("Student:", student)
    st.write(f"Confidence: {confidence:.1f}%")
    st.divider()
    st.write(register)
        
