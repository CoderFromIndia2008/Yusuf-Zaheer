import os, base64, streamlit as st, streamlit.components.v1 as components
from list import students
from drive_access import upload

video_recorder = components.declare_component(
    'video_recorder',
    path = os.path.join(os.path.dirname(__file__), 'video_recorder_component')
)

if 'student' not in st.session_state:
    selected = st.selectbox('Select your name:', students, index = None, placeholder = 'Search your roll number or name...')

    if selected and st.button('Continue'):
        st.session_state['student'] = selected
        st.session_state.pop('rec_id', None)
        st.rerun()

if 'student' in st.session_state:
    student = st.session_state['student']
    st.success(f'Beginning registeration for {student.split(".", 1)[1]}')

    if 'video' not in st.session_state:
        st.success('Please click record video below to initiate capture process')
        rec_id = st.session_state.get('rec_id', 0)
        video = video_recorder(default = None, key = f'rec_{rec_id}')

        if video:
            st.session_state['video'] = video
            st.rerun()

    if 'video' in st.session_state:
        webm = f'{student.split('.')[0]}.webm'
        video_bytes = base64.b64decode(st.session_state['video'])

        open(webm, 'wb').write(video_bytes)

        st.success('Video received successfully!')
        st.success('Check your captured video below')
        st.video(video_bytes)
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button('Upload Video'):
                try:
                    upload(webm)
                    st.success('Video sent successfully for model training!')
                    st.success('You may close this page safely')
                    del st.session_state['video']

                except Exception as e:
                    st.error(f'Upload failed: {e}')

                finally:
                    if os.path.exists(webm):
                        os.remove(webm)

        with col2:
            if st.button('Recapture'):
                del st.session_state['video']

                if os.path.exists(webm):
                    os.remove(webm)
                st.session_state['rec_id'] = st.session_state.get('rec_id', 0) + 1
                st.rerun()