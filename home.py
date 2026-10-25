import streamlit as st
import utils
import core
import time

text = utils.pretty("Home", colour="violet", icon="home")
st.set_page_config(text)

utils.title(
"Home", 
"home", 
"Summary of today's attendance and learn about the project."
)

st.sidebar.title(":violet[**:material/familiar_face_and_zone: AI Attendance**]")
st.sidebar.caption("Attendance Marking and Management System with AI.")
st.sidebar.divider()

utils.subheader("Today's overview", "today")

st.caption(f"Attendance for {utils.date} {utils.month[:3]} {utils.year}")

session = utils.GetSession()
if session not in utils.sessions:
    register = None
    
else:
    register = core.ViewRegister(utils.date, utils.month, session)

if register is None:
    st.info(f"No attendance available for today.")

else:
    total_strength = register.shape[0]
    present = sum(register[str(utils.date)] == "P")
    absent = sum(register[str(utils.date)] == "A")
    percent = present / total_strength * 100
    
    col1, col2, col3 = st.columns(3, border=True)
    
    with col1:
        utils.metric("Present Today", f"{present}/{total_strength}", "green")
    
    with col2:
        utils.metric("Absent Today", f"{absent}/{total_strength}", "red")
    
    with col3:
        utils.metric("Percent %", f"{percent:.1f}%", "gray")
    
    st.divider()
    
    utils.subheader("Today's register", "table")

    utils.Display(register, session)
    st.divider()

utils.subheader("Purpose", "potted_plant")
    
st.write("""
The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
this reduces the responsibilities of the teacher and gives them more room to breathe before classes begin.
""")
    
utils.subheader("Working", "manufacturing")
    
st.markdown("""
- Images are collected on which classification is done, the collection is through streamlit's file_uploader() and camera_input().
- Some preprocessing is done before classification to improve accuracy.
- Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade.
- The classification model to recognise the identity of students is a CNN model. It uses adam as the optimizer, sparse_binary_crossentropy for loss and has total ... parameters.
- Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Pandas' DataFrames.
""")
    
utils.subheader ("Team", "diversity_3")
    
with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1: utils.designation("Arush", "Data Expert")
    with col2: utils.designation("Aryan", "Video Producer")

    col3, col4 = st.columns(2)
    with col3: utils.designation("Jaffer", "Information Researcher")
    with col4: utils.designation("Krishna", "Communication Leader")
        
    col5, col6 = st.columns(2)
    with col5: utils.designation("Yusuf", "Main Coder")
    with col6: utils.designation("Zoheb", "Web Designer")
        
utils.subheader("Video", "movie")
#st.video("/workspaces/Yusuf-Zaheer/our_video.mov")

utils.subheader("Resources & Acknowledgement", "menu_book")
    
st.write("""
- [Deep Learning course by FreeCodeCamp](https://youtu.be/IA3WxTTPXqQ)
- [OpenCV course by FreeCodeCamp](https://youtu.be/oXlwWbU8l2o)
- [Deep Learning course by Kaggle](https://www.kaggle.com/learn/intro-to-machine-learning)
- [Streamlit course by RyanAndMattDataScience](https://youtu.be/eAgONwZ_dKM)
- And many more sources were used.
- The support of our teachers, friends and families was also vital to the success of this project.
""")

with st.expander("Easter Egg", type="compact"):
    st.write(":gray[Do You Like Balloons?]")
    if st.button(":green[**Yes**]"):
        for i in range(5):
            st.balloons()
            time.sleep(0.75)
            
            