import tensorflow as tf 
import pathlib as pt
import pandas as pd
import numpy as np
import time

#base_dir = pt.Path("/workspaces/Yusuf-Zaheer")
base_dir = pt.Path("/mount/src/Yusuf-Zaheer/")
data_dir = base_dir / "database"
tools_dir = base_dir / "tools"

full_months = ["January", "February", "March", "April", "May", "June", 
"July", "August", "September", "October", "November", "December"]

def get_time():
    return time.strftime("%d %B %Y").split()
    
def mark(img, model, img_size=224):
    with open(data_dir / "prediction_target.jpg", "wb") as file:
        file.write(img.getbuffer())

    date, month, year = get_time()
    year_dir = data_dir / str(year)
    meta_path = year_dir / "metadata.csv"
    register_path = year_dir / f"{month}.csv"
    
    if not register_path.exists():
        year_dir.mkdir(exist_ok=True)
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
    
def view(date, month, year):   
    register_path = data_dir / f"{year}/{month}.csv"
    
    try:
        register = pd.read_csv(register_path)
        
    except FileNotFoundError:
        year_dir = data_dir / str(year)
        
        if year_dir.exists():
            return "No attendance available for this month"
        
        return "No attendance available for this year"
        
    if date != 0:
        if str(date) in register.columns:
            columns = ["name", str(date)]
            register = register.set_index(register["roll"])
            
            return register[columns]
        
        else:
            return "No attendance available for this date"
            
    register = register.set_index(register["roll"]).drop("roll", axis=1)
    return register
    
def percent(month1, month2, year):
    month1_idx = full_months.index(month1)
    month2_idx = full_months.index(month2) + 1
    
    months = full_months[month1_idx:month2_idx]
    
    year_dir = data_dir / str(year)
    meta_path = year_dir / "metadata.csv"
    
    if not year_dir.exists():
        return (0, "No attendance available for this year")
        
    working_days = 0
    percent_df = pd.read_csv(meta_path)
    percent_df["Total"] = ""
    for month in months:
        register_path = year_dir / f"{month}.csv"
        
        if not register_path.exists():
            continue
            
        register = pd.read_csv(register_path)
        
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
        
    percent_df = percent_df.set_index(percent_df["roll"]).drop("roll", axis=1)
    return (working_days, percent_df)
    
def remove(name, options):
    index_remove = options.index(name)
    date, month, year = get_time()
    meta_path = data_dir / f"{year}/metadata.csv"

    if not meta_path.exists():
        return "No students registered yet"
    
    names = pd.read_csv(meta_path)        
    names = names.drop(index_remove, axis=0)
    names.iloc[index_remove:, 0] -= 1
    names.to_csv(meta_path, index=False)
    names = names.set_index(names["roll"]).drop("roll", axis=1)
    return names
            
def deleted(df, year):
    truth = []
    meta_path = data_dir / f"{year}/metadata.csv"
    register = pd.read_csv(meta_path)
    full_names = tuple(register["name"])
    mismatch = len(full_names) != register.shape[0]
            
    if not mismatch:
        return (mismatch, df)
        
    for idx in df.index:
        truth.append(df.loc[idx, "name"] in full_names)

    cleaned = df[truth]
    cleaned["roll"] = range(1, sum(truth) + 1)
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

def get_current_month(year):
    year_dir = data_dir / str(year)
    months = [m.stem for m in year_dir.iterdir() if m.is_file()]

    for idx, month in enumerate(full_months[-1::-1]):
        if month in months:
            return 11 - idx
