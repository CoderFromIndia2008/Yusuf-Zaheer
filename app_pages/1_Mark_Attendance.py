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
    
if not img:
    st.stop()

st.success("Capture successful!")

student, confidence, register = core.MarkAttendance(img)

if register is None:
    st.stop()

st.success("Prediction successful!")
col1, col2 = st.columns(2)
col1.metric("Student", student)
col2.metric("Confidence", f"{confidence:.1f}%")
st.divider()
st.write(register.set_index("roll"))
            
