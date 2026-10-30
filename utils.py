import streamlit as st
import pathlib as pt
import random as rn
import pandas as pd
import datetime
import pickle
import cv2

#important files and directories
base_dir = pt.Path.cwd()
data_dir = base_dir / "database"
tools_dir = base_dir / "tools"
password_path = tools_dir / "password.dat"

#time
now = datetime.datetime.now()
hour, minute, day, date, month, year = now.strftime("%h %M %a %d %B %Y").split()
full_months = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"]
months_ordered = full_months[9:] + full_months[:9]
cur_month_idx = full_months.index(month)

def getDay(date, month, session):
    year = int(session[-2:]) if month in full_months[9:] else int(session[-2:]) - 1
    day = datetime.date(year, months_ordered.index(month)+1, int(date))
    return day.strftime("%a")

#session management
sessions = [s.name for s in data_dir.iterdir() if s.is_dir()]
sessions.sort(reverse=True, key=lambda x: int(x[-2:]))

def getSession(m=month, y=year):
    y = int(y[-2:])
        
    if m in ["January", "February", "March"]:
        y -= 1

    return data_dir / f"20{y}-{y+1}"
    
#read a file
def getFile(*arg, type):
    if type == "register":
        arg = arg or [month, getSession().name]
        m, s = arg[0], arg[1]
        idx = full_months.index(m)+1
        path = data_dir / s / f"{idx}_{m}_{s}.csv"
        
    elif type == "meta":
        arg = arg or [getSession().name]
        session = arg[0]
        path = data_dir / session / f"metadata_{session}.csv"
        
    if not path.exists():
        return (None, path)
        
    return (pd.read_csv(path), path)

#colour
def colour(value):
    if value == "P":
        return "background-color: #D4EDDA; color: #155724"

    elif value == "A":
        return "background-color: #F8D7DA; color: #721C24"

    return ""

#pagintion
def pagination(df, column_order=None, hide_index=None):
    rows_per_page = 10
    total_pages = (len(df) + rows_per_page - 1) // rows_per_page

    slot = st.empty()
    with st.container(horizontal_alignment="right"):
        page = st.pagination(num_pages=total_pages, key="pagination")

    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    slot.dataframe(df.iloc[start_idx:end_idx].style.map(colour), key="display")
    
#display a register if exists, choose to display with/without removed students
def display(original, session, return_df=False):
    if original is None:
        st.error("No attendance available.")
        return None
        
    metadata, _ = getFile(session, type="meta")
    names = tuple(metadata["name"])
    exist = []
    for idx in original.index:
        exist.append(original.loc[idx, "name"] in names)

    if (not all(exist)) and st.toggle("Display removed student(s)"):
        df = original.set_index("roll")

    else:
        df = original[exist]
        df["roll"] = tuple(metadata["roll"])    
        df = df.set_index("roll")
            
    if return_df:
        return df
    
    pagination(df)

#page headings and text styling
def title(value, icon, desc):        
    st.title(f":violet[:material/{icon}: {value}]")
    st.caption(desc)
    st.divider()
    
def subheader(name, icon, desc=None, divider=True):
    st.subheader(f"**:blue[:material/{icon}: {name}]**")
    if desc:
        st.caption(desc)
        st.write("")
        if divider:
            st.divider()
    else:
        st.write("")

def metric(title, value, colour):
    st.metric(f":{colour}[**{title}**]", value)  

def designation(name, title):
    st.markdown(f"**{name}**")
    st.caption(f"{title}")
    
def pretty(value, colour, bold=False, icon=None):
    if icon and bold:
        return f":{colour}[**:material/{icon}: {value}**]"
        
    if icon:
        return f":{colour}[:material/{icon}: {value}]"
    
    if bold:
        return f":{colour}[**{value}**]"
        
    return f":{colour}[{value}]"

#selection
def selectDate(key, default=int(date)):
    d = st.number_input(
        "Choose a date (0 = whole month)", 
        min_value=0, 
        max_value=31, 
        step=1, 
        value=default, 
        key=key
    )

    return d
    
def selectMonth(title, key, options=full_months, default=cur_month_idx):
    m = st.selectbox(title, options, index=default, key=key)
    return m

#password management
text = pretty("Authentication Required", "violet", True, "key")

@st.dialog(text)
def password():
    user = st.text_input("Enter password", type="password")
    password_exists = password_path.exists()

    if not password_exists and st.button("Set Password", width="stretch", type="primary"):
        file = open(password_path, "wb")        
        pickle.dump(user, file)
        file.close()
        password_exists = True
        
    elif password_exists and st.button("Submit Password", width="stretch", type="primary"):
        file = open(password_path, "rb")
        password = pickle.load(file)
        file.close()
        
        st.session_state["key"] = user == password

        if st.session_state["key"] == False:
            st.error("Wrong password.")
        
    if st.session_state["key"] == True:
        st.rerun()
    
#image preprocessing
yunet_path = tools_dir / "models/face_detection.onnx"
detector = cv2.FaceDetectorYN.create(yunet_path, "", (320, 320), 0.5, 0.3, 5000)

def process(img=None, path=None, rotate=False, save=False):
    if img is None:
        img = cv2.imread(path)

    h, w = img.shape[:2]
    detector.setInputSize((w, h))
    faces = detector.detect(img)[1]
    
    if faces is None:
        st.errir("No face found.")
        return None
        
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])[:4]
    x, y, fw, fh = map(int, (x, y, fw, fh))
    
    pad_x = int(fw * 0.25)
    pad_y = int(fh * 0.25)
    
    left = max(0, x - pad_x)
    top = max(0, y - pad_y)
    
    right = min(w, x + fw + pad_x)
    bottom = min(h, y + fh + pad_y)
    crop = img[top:bottom, left:right]
    
    if crop.size == 0:
        st.error("Invalid face crop.")
        return None
        
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    equal = cv2.equalizeHist(gray)
    face = cv2.resize(equal, (224, 224), interpolation = cv2.INTER_AREA)
    
    if rotate:
        h, w = face.shape[:2]
        angle = rn.randint(10, 15) * rn.choice([1, -1])
        rotation_matrix = cv2.getRotationMatrix2D((w/2,h/2), angle, 1)
        face = cv2.warpAffine(face, rotation_matrix, (w, h))
        
    if save:
        cv2.imwrite(path, face)
        
    return face