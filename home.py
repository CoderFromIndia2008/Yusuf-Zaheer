import streamlit as st
import time
import core

def home():
    st.subheader(":blue[:material/potted_plant: Purpose]")

    st.write("""The project aims to provide a way for teachers to mark attendance through an automatic AI based system,
    this reduces the responsibilities of the teacher and gives them more room to breathe before classes begin.""")

    st.subheader(":blue[:material/manufacturing: Working]")

    st.markdown("""
    - Images are collected on which classification is done, the collection is through streamlit's file_uploader() and camera_input().
    - Some preprocessing is done before classification to improve accuracy.
    - Before the classification, the images are cropped to only include the faces and not uneccessary background details, this is done using Haar Cascade.
    - The classification model to recognise the identity of students is a CNN model. It uses adam as the optimizer, sparse_binary_crossentropy for loss and has total ... parameters.
    - Rest of the code, which offers extra features like viewing attendance register, attendance percentage, quickly registering and removing students is done through Pandas' DataFrames.
    """)

    st.subheader(":blue[:material/diversity_3: Team]")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        col1.markdown("**Arush**")
        col1.caption("Data Expert")
        col2.markdown("**Aryan**")
        col2.caption("Video Producer")

        col3, col4 = st.columns(2)
        col3.markdown("**Jaffer**")
        col3.caption("Information Researcher")
        col4.markdown("**Krishna**")
        col4.caption("Communication Leader")

        col5, col6 = st.columns(2)
        col5.markdown("**Yusuf**")
        col5.caption("Main Coder")
        col6.markdown("**Zoheb**")
        col6.caption("Web Designer")

    st.subheader(":blue[:material/movie: Video]")
    #st.video("/workspaces/attendance-system/our_video.mov")

    st.subheader(":blue[:material/menu_book: Resources]")
    st.write("""
    - [Deep Learning course by FreeCodeCamp](https://youtu.be/IA3WxTTPXqQ)
    - [OpenCV course by FreeCodeCamp](https://youtu.be/oXlwWbU8l2o)
    - [Deep Learning course by Kaggle](https://www.kaggle.com/learn/intro-to-machine-learning)
    - [Streamlit course by RyanAndMattDataScience](https://youtu.be/eAgONwZ_dKM)
    - And many more sources were used.
    - The support of our teachers, friends and families was also vital to the success of this project.
    """)

    with st.expander("Easter Egg", type="compact"):
        if core.month in ["December", "January"]:
            st.write(":blue[Do you like snow?]")
            run = st.snow
        else:
            st.write(":blue[Do You Like Balloons?]")
            run = st.balloons
        if st.button(":green[**Yes**]"):
            for i in range(5):
                run()
                time.sleep(0.75)

def ascii():
    st.markdown("""
                                                  ,o88888
                                               ,o8888888'
                         ,:o:o:oooo.        ,8O88Pd8888"
                     ,.::.::o:ooooOoOoO. ,oO8O8Pd888'"
                   ,.:.::o:ooOoOoOO8O8OOo.8OOPd8O8O"
                  , ..:.::o:ooOoOOOO8OOOOo.FdO8O8"
                 , ..:.::o:ooOoOO8O888O8O,COCOO"
                , . ..:.::o:ooOoOOOO8OOOOCOCO"
                 . ..:.::o:ooOoOoOO8O8OCCCC"o
                    . ..:.::o:ooooOoCoCCC"o:o
                    . ..:.::o:o:,cooooCo"oo:o:
                 `   . . ..:.:cocoooo"'o:o:::'
                 .`   . ..::ccccoc"'o:o:o:::'
                :.:.    ,c:cccc"':.:.:.:.:.'
              ..:.:"'`::::c:"'..:.:.:.:.:.'
            ...:.'.:.::::"'    . . . . .'
           .. . ....:."' `   .  . . ''
         . . . ...."'
         .. . ."'     -hrr-
        .
    """)