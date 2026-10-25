import streamlit as st
import pandas as pd
import numpy as np
import utils

#mark student attendance using face recignition (cnn model in tools/models)
@st.cache_resource()
def LoadModel():
    import tensorflow as tf 
    return tf.keras.models.load_model(utils.tools_dir / f"models/face_recognition.keras")   

def MarkAttendance(img):
    img_path = utils.tools_dir / "etc/prediction_target.png"
    with open(img_path, "wb") as file:
        file.write(img.getbuffer())
        
    img = utils.process(path=img_path, save=True)
    if img is None:
        st.error("No faces detected/image not found.")
        return (None, None, None)

    register, path = utils.GetFile(type="register")
    if register is None:
        register, path = utils.GetFile(type="meta")
        
        if register is None:
            st.error("No students registered")
            return (None, None, None)
  
    if not utils.date in register.columns:
        register.loc[:, utils.date] = "A"

    model = LoadModel()
    img = tf.keras.utils.load_img(img_path, target_size=(224,224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    
    predicted = model.predict(img_array)[0]
    students = list(register["name"])
    idx = np.argmax(predicted)
    confidence = max(predicted)
    
    register.loc[idx, utils.now.day] = "P"            
    register.to_csv(path, index=False)
    
    columns = ["roll", "name", utils.now.day]
    return (register[columns], students[idx], confidence*100)
    
#view attendance register for any date, month and session
def ViewRegister(date, month, session):   
    register, _ = utils.GetFile(month, session, type="register")
    if register is None:
        return None
        
    if date == 0:
        return register
        
    if not str(date) in register.columns:
        return None
            
    columns = ["roll", "name", str(date)]
    return register[columns]
    
#show attendance total and percentage of all students in a month range
def AttendancePercent(from_month, to_month, session):
    from_idx = utils.full_months.index(from_month)
    to_idx = utils.full_months.index(to_month) + 1
    months = utils.full_months[from_idx:to_idx]
    
    working_days = 0
    percent_df = pd.DataFrame()

    for month in months:
        register, _ = utils.GetFile(month, session, type="register")
        
        if register is None:
            continue
        
        elif working_days == 0:
            percent_df = register[["roll", "name"]]
            percent_df["Total"] = ""
        
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            percent_df["Total"] += register[column]

    if working_days == 0:
        return (None, 0)

    for idx, row in enumerate(percent_df["Total"]):
        percent_df.loc[idx, "Total"] = str(row.count("P"))
        percent_df.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"
        
    return (percent_df, working_days)
    
def MonthWiseRegister(idx, session):
    month_wise = pd.DataFrame([("", 0, 0.0, "red") for i in range(12)], index=utils.full_months, columns=("str", "Total", "%", "colour"))

    for month in utils.full_months:
        register, path = utils.GetFile(month, session, type="register")

        if register is None:
            continue

        working_days = len(register.columns) - 2
        for column in register.columns[2:]:
            month_wise.loc[month, "str"] += register.loc[idx, column]
        
        month_wise.loc[month, "Total"] = month_wise.loc[month, "str"].count("P")
        month_wise.loc[month, "%"] = month_wise.loc[month, "Total"] * 100 / working_days

        if month_wise.loc[month, "%"] >= 80:
            month_wise.loc[month, "colour"] = "green"

        elif month_wise.loc[month, "%"] >= 60:
            month_wise.loc[month, "colour"] = "yellow"

    return month_wise