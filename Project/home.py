def home():
    import streamlit as st

    st.subheader(":blue[:material/potted_plant: Purpose:]")

    st.write("""The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
    this reduces the responsibilities of the teacher and gives them more room to breathe before classes begin.""")

    st.subheader(":blue[:material/manufacturing: Working:]")

    st.markdown("""
    - Images are collected on which classification is done, the collection is through streamlit's file_uploader() and camera_input().
    - Some preprocessing is done before classification to improve accuracy.
    - Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade.
    - The classification model to recognise the identity of students is a CNN model. It uses adam as the optimizer, sparse_binary_crossentropy for loss and has total ... parameters.
    - Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Pandas' DataFrames.
    """)

    st.subheader(":blue[:material/diversity_3: Made by:]")

    st.write("""
    - Arush (Data Expert)
    - Aryan Vishwakarma (Video Producer)
    - Jaffar (Information Researcher)
    - Krishna V. Gupta (Communication Leader)
    - Yusuf Zaheer (Main Coder)
    - Zoheb Arsh (Web Designer)
    """)

    st.subheader(":blue[:material/movie: Video]:")
    #st.video("/workspaces/attendance-system/our_video.mov")

    st.subheader(":blue[:material/menu_book: Resources:]")
    st.write("""
    - [Deep Learning course by FreeCodeCamp](https://youtu.be/IA3WxTTPXqQ)
    - [OpenCV course by FreeCodeCamp](https://youtu.be/oXlwWbU8l2o)
    - [Deep Learning course by Kaggle](https://www.kaggle.com/learn/intro-to-machine-learning)
    - [Streamlit course by RyanAndMattDataScience](https://youtu.be/eAgONwZ_dKM)
    - And many more sources were used.
    - The support of our teachers, friends and families was also vital to the success of this project.
    """)

    import time
    with st.expander("Easter Egg"):
        st.write(":blue[Do You Like Balloons?]")
        if st.button(":green[**Yes**]"):
            for i in range(5):
                st.balloons()
                time.sleep(0.7)
