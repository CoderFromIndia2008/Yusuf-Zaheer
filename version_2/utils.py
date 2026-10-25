import streamlit as st
import pathlib as pt
import random as rn
import pandas as pd
import pickle
import time
import cv2

#IMPORTANT FILES/DIRECTORIES
base_dir = pt.Path("/workspaces/Yusuf-Zaheer")
data_dir = base_dir / "database"
tools_dir = base_dir / "tools"
password_path = tools_dir / "password.dat"

#TIME
hour, minute, date, month, year = time.strftime("%h %M %d %B %Y").split()
full_months = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"]

if "month" not in st.session_state:
    st.session_state["month"] = month 

cur_month_idx = full_months.index(month)

#SESSIONS
sessions = [s.name for s in data_dir.iterdir() if s.is_dir()]
sessions.sort(reverse=True, key=lambda x: int(x[-2:]))

if "session" not in st.session_state:
    if len(sessions) != 0:
        st.session_state["session"] = sessions[-1]

#SESSION MANAGEMENT
def GetSession(m=None, y=None):
    m, y = m or month, y or year
    y = int(y[-2:])
        
    if m in ["January", "February", "March"]:
        y -= 1

    return data_dir / f"20{y}-{y+1}"
    
#FILE MANAGEMENT
def GetFile(*arg, type):
    if type == "register":
        arg = arg or [month, GetSession()]
        month, session = arg[0], arg[1]
        idx = full_months.index(month)+1
        path = data_dir / session / f"{idx}_{month}_{session}.csv"
        
    elif type == "meta":
        arg = arg or [GetSession()]
        session = arg[0]
        path = data_dir / session / f"metadata_{session}.csv"
        
    if not path.exists():
        return (None, path)
        
    return (pd.read_csv(path), path)
        
#DISPLAY REGISTER WITH/WITHOUT REMOVED STUDENTS
def Display(original, session):
    if original is None:
        st.error("No attendance available")
        return None
        
    metadata, _ = GetFile(session, type="meta")
    names = tuple(metadata["name"])
    exist = []
    for idx in original.index:
        exist.append(original.loc[idx, "name"] in names)

    if (not all(exist)) and st.toggle("Display removed student(s)"):
        st.write(original.set_index("roll"))
        return None

    modified = original[exist]
    modified["roll"] = tuple(metadata["roll"])    
    st.write(modified.set_index("roll"))
        
#PAGE HEADINGS
def title(value, icon, desc, config=True):
    if config:
        st.set_page_config(value)
        
    st.title(f":violet[:material/{icon}: {value}]")
    st.caption(desc)
    st.divider()
    
def subheader(name, icon):
    st.subheader(f":blue[:material/{icon}: {name}]")
    
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
    
#PASSWORD MANAGEMENT
if "key" not in st.session_state:
        st.session_state["key"] = False

@st.dialog(":violet[:material/key: Authentication Required]")
def Password():
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
        
    if st.session_state["key"] == True:
        st.rerun()
    
#IMAGE PREPROCESSING
path = tools_dir / "yunet.onnx"
detector = cv2.FaceDetectorYN.create(path, "", (320, 320), 0.5, 0.3, 5000)

def process(img=None, path=None, rotate=False, save=False):
    if img is None:
        img = cv2.imread(path)

    h, w = img.shape[:2]
    detector.setInputSize((w, h))
    faces = detector.detect(img)[1]
    
    if faces is None:
        st.errir("No face found")
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
        st.error("Invalid face crop")
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

    