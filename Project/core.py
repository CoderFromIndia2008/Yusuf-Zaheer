import tensorflow as tf 
import pathlib as pt
import pandas as pd
import numpy as np
import time

#base_dir = pt.Path("/workspaces/Yusuf-Zaheer")
base_dir = pt.Path("/mount/src/yusuf-zaheer/")
data_dir = base_dir / "database"
tools_dir = base_dir / "tools"

full_months = ["April", "May", "June", "July", "August", "September", 
               "October", "November", "December", "January", "February", "March"]

def get_time():
    return time.strftime("%d %B %y").split()

def get_register_path(session, month):
    register_path = data_dir / session / f"{full_months.index(month)+1}_{month}_{session}.csv"
    return register_path

def get_meta_path(session):
    meta_path = data_dir / session / f"metadata_{session}.csv"
    return meta_path

def get_session_dir(year):
    year = int(year)
    session_dir = data_dir / f"20{year}-{year+1}"
    return session_dir

def get_month_path(session, month):
    register_path = data_dir / session / f"{full_months.index(month)+1}_{month}_{session}.csv"
    return register_path
    
def mark(img, model, img_size=224):
    with open(data_dir / "prediction_target.jpg", "wb") as file:
        file.write(img.getbuffer())

    date, month, year = get_time()

    if month in ["January", "February", "March"]:
        year -= 1

    session_dir = get_session_dir(year)
    register_path = get_register_path(session_dir.name, month)
    meta_path = get_meta_path(session_dir.name)    

    if not register_path.exists():
        session_dir.mkdir(exist_ok=True)
        register = pd.read_csv(meta_path)
        
    else:
        register = pd.read_csv(register_path)
  
    if not date in register.columns:
        register.loc[:, date] = "A"

    model = tf.keras.models.load_model(tools_dir / f"models/{model}.keras")
    img_path = data_dir / "prediction_target.jpg"
    
    img = tf.keras.utils.load_img(img_path, target_size=(img_size, img_size))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    confidence = round(np.max(score)*100, 1)

    classes = list(register["name"])
    student = classes[np.argmax(score)]
    idx = register.index[np.argmax(score)] 
    
    register.loc[idx, date] = "P"            
    register.to_csv(register_path, index=False)

    columns = ["roll", "name", str(date)]
    return (student, confidence, register[columns])
    
def view(date, month, session):   
    register_path = get_register_path(session, month)
    session_dir = data_dir / session

    try:
        register = pd.read_csv(register_path)
        
    except FileNotFoundError:        
        if session_dir.exists():
            return "No attendance available for this month"
        
        return "No attendance available for this year"
        
    if date != 0:
        if str(date) in register.columns:
            columns = ["roll", "name", str(date)]
            
            return register[columns]
        
        else:
            return "No attendance available for this date"
            
    return register
    
def percent(month1, month2, session):
    month1_idx = full_months.index(month1)
    month2_idx = full_months.index(month2) + 1
    months = full_months[month1_idx:month2_idx]
    session_dir = data_dir / session
    meta_path = get_meta_path(session)    

    if not session_dir.exists():
        return (0, "No attendance available for this year")
        
    working_days = 0
    percent_df = None

    for month in months:
        register_path = get_register_path(session, month)
        
        if not register_path.exists():
            continue
            
        register = pd.read_csv(register_path)
        if percent_df == None:
            percent_df = register[["roll", "name"]]
            percent_df["Total"] = ""
        
        #register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            percent_df["Total"] += register[column]

    if working_days == 0:
        return (0, "No attendance for the given month(s)")

    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(percent_df["Total"]):
        percent_df.loc[idx, "Total"] = str(row.count("P"))
        percent_df.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"
        
    return (working_days, percent_df)
    
def remove(name, options):
    index_remove = options.index(name)
    _, _, year = get_time()
    session_dir = get_session_dir(year)
    meta_path = get_meta_path(session_dir.name)

    if not meta_path.exists():
        return "No students registered yet"
    
    names = pd.read_csv(meta_path)        
    names = names.drop(index_remove, axis=0)
    names.iloc[index_remove:, 0] -= 1
    names.to_csv(meta_path, index=False)
    return names
            
def deleted(df, session):
    truth = []
    meta_path = get_meta_path(session)
    register = pd.read_csv(meta_path)
    full_names = tuple(register["name"])
    mismatch = len(full_names) != df.shape[0]
            
    if not mismatch:
        return (mismatch, df)
        
    for idx in df.index:
        truth.append(df.loc[idx, "name"] in full_names)

    cleaned = df[truth]
    cleaned["roll"] = range(1, cleaned.shape[0]+1)

    return (mismatch, cleaned)
    
def password(user_input):
    import pickle
    password_path = tools_dir / "password.dat"

    if not password_path.exists():
        file = open(password_path, "wb")
        pickle.dump((user_input, ), file)
        file.close()

    file = open(password_path, "rb")
    true_password = str(pickle.load(file)[0])
    return user_input == true_password

def get_current_month(session):
    session_dir = data_dir / session
    months = [m.stem for m in session_dir.iterdir() if m.is_file()]
    months = [m.strip("1234567890-_") for m in months]
    
    for month in full_months[-1::-1]:
        if month in months:
            return full_months.index(month)