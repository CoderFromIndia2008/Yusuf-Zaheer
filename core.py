import tensorflow as tf
import pathlib as pt
import pandas as pd
import numpy as np
import functools
import pickle
import time

base_dir = pt.Path.cwd()
data_dir = base_dir / "database"
tools_dir = base_dir / "tools"
minute, hour, date, month, year = time.strftime("%M %H %d %B %y").split()
year = int(year)
full_months = ["April", "May", "June", "July", "August", "September", 
               "October", "November", "December", "January", "February", "March"]

#month = "December"

def GetRegisterPath(session, month):
    return data_dir / session / f"{full_months.index(month)+1}_{month}_{session}.csv"

def GetMetaPath(session):
    return data_dir / session / f"metadata_{session}.csv"

def GetSessionDir(year):
    return data_dir / f"20{year}-{year+1}"
    
def GetSessionList():
    sessions = []
    for session in data_dir.iterdir():
        if session.is_dir():
            sessions.append(session.name)
            
    sessions.sort(reverse=True, key=lambda x: int(x[-2:]))
    return sessions

def GetSession(year, month):
    if month in ["January", "February", "March"]:
        year -= 1

    return f"20{year}-{year+1}"

    
def GetCurrentMonth(session):
    session_dir = data_dir / session
    months = [m.stem for m in session_dir.iterdir() if m.is_file()]
    months = [m.strip("1234567890-_") for m in months]
    
    for month in full_months[-1::-1]:
        if month in months:
            return full_months.index(month)
    return 0

#I am using this decorator to reduce loading time
@functools.lru_cache(maxsize=1)
def LoadModel(name):
    import tensorflow as tf 
    return tf.keras.models.load_model(tools_dir / f"{name}.keras")

def MarkAttendance(img, model_name, img_size=224):
    img_path = tools_dir / "prediction_target.png"
    
    with open(img_path, "wb") as file:
        file.write(img.getbuffer())

    #importing here to avoid circular import
    import preprocessor
    img = preprocessor.process(path=img_path, save=True)
    if img is None:
        return (None, None, None)

    session = GetSession(year, month)
    session_dir = data_dir / session
    register_path = GetRegisterPath(session_dir.name, month)
    meta_path = GetMetaPath(session_dir.name)    

    if not register_path.exists():
        session_dir.mkdir(exist_ok=True)
        register = pd.read_csv(meta_path)
        
    else:
        register = pd.read_csv(register_path)
  
    if not date in register.columns:
        register.loc[:, date] = "A"

    model = LoadModel(model_name)
    
    img = tf.keras.utils.load_img(img_path, target_size=(img_size, img_size))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    
    predicted = model.predict(img_array)[0]
    students = list(register["name"])
    idx = np.argmax(predicted)
    confidence = max(predicted)
    
    register.loc[idx, date] = "P"            
    register.to_csv(register_path, index=False)

    print({"pred":predicted, "confidence":confidence, "idx":idx, "student":students[idx]})
    
    columns = ["roll", "name", date]
    return students[idx], confidence, register[columns]
    
def ViewRegister(date, month, session):   
    register_path = GetRegisterPath(session, month)
    
    if not register_path.exists():
        return None

    register = pd.read_csv(register_path)
        
    if date == 0:
        return register
        
    if not str(date) in register.columns:
        return None
            
    columns = ["roll", "name", str(date)]
    return register[columns]
    
def AttendancePercent(from_month, to_month, session):
    session_dir = data_dir / session
    
    from_idx = full_months.index(from_month)
    to_idx = full_months.index(to_month) + 1
    months = full_months[from_idx:to_idx]
        
    working_days = 0
    percent_df = pd.DataFrame()

    for iter, month in enumerate(months):
        register_path = GetRegisterPath(session, month)
        
        if not register_path.exists():
            continue
            
        register = pd.read_csv(register_path)
        
        if iter == 0:
            percent_df = register[["roll", "name"]]
            percent_df["Total"] = ""
        
        #register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            percent_df["Total"] += register[column]

    if working_days == 0:
        return (0, None)

    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(percent_df["Total"]):
        percent_df.loc[idx, "Total"] = str(row.count("P"))
        percent_df.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"
        
    return (working_days, percent_df)
    
def RemoveStudent(idx):
    session_dir = GetSessionDir(year)
    meta_path = GetMetaPath(session_dir.name)
    if not meta_path.exists():
        return None
        
    metadata = pd.read_csv(meta_path)
    metadata = metadata.drop(idx, axis=0)
    metadata.iloc[idx:, 0] -= 1
    metadata.to_csv(meta_path, index=False)
    return metadata
            
def AdjustNames(original, session):
    #incase a student has been struck off from the attendance register, 
    #this function allows the user to choose,
    #whether to see attendance for that student or not.
    
    truth = []
    meta_path = GetMetaPath(session)
    register = pd.read_csv(meta_path)
    full_names = tuple(register["name"])
    mismatch = len(full_names) != original.shape[0]
            
    if not mismatch:
        return (mismatch, original)
        
    for idx in original.index:
        truth.append(original.loc[idx, "name"] in full_names)

    modified = original[truth]
    modified["roll"] = range(1, modified.shape[0]+1)
    return (mismatch, modified)
    
def PasswordVerify(user_input=None):
    password_path = tools_dir / "password.dat"

    if user_input == None:
        message = "Submit password"
        if not password_path.exists():
            message = "Set password"
        return message
    
    if not password_path.exists():
        file = open(password_path, "wb")
        pickle.dump((user_input, ), file)
        file.close()

    file = open(password_path, "rb")
    true_password = str(pickle.load(file)[0])
    return user_input == true_password
    
