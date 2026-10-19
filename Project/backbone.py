import tensorflow as tf
import pathlib as pt
import pandas as pd
import numpy as np
import time

dbpath = pt.Path("/workspaces/Yusuf-Zaheer/database")
toolpath = pt.Path("/workspaces/Yusuf-Zaheer/tools")
metapath = dbpath / "metadata.csv"

full_months = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

def mark(img, model):
    """
    This function marks student attendance.
    
    Input:
        img(object) = Requires an image object from which student can be identified. 
        model(string) = The model name must be provided, predictions may vary based on the model selected.
    
    Output: a tuple with three elements
        0. student(string) = predicted student identity.
        1. confidence(float) = confidence of model in student's predicted identity
        2. register(dataframe) = register with the attendance marked
    """
    
    with open(dbpath / "current_prediction_target.png", "wb") as file:
        file.write(img.getbuffer())

    date, month, year = time.strftime("%d-%B-%Y").split("-")
    img_size = 224
    yearpath = dbpath / str(year)
    path = yearpath / f"{month}.csv"
    
    if not yearpath.exists() or not path.exists():
        yearpath.mkdir(exist_ok=True)
        register = pd.read_csv(metapath)
        
    else:
        register = pd.read_csv(path)
  
    if not date in register.columns:
        register.loc[:, date] = "A"

    #tool model and load image
    #convert image to a usable format
    model = tf.keras.models.load_model(toolpath / f"{model}.keras")
    img_path = dbpath / "current_prediction_target.png"
    img = tf.keras.utils.load_img(img_path, target_size=(img_size, img_size))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    score = tf.nn.softmax(predictions[0])

    classes = list(register["name"])
    student = classes[np.argmax(score)]
    
    student_idx = list(register.index)
    idx = student_idx[np.argmax(score)] 
    
    register.loc[idx, date] = "P"            
    register.to_csv(path, index=False)
    
    confidence = round(np.max(score)*100, 2)
    
    return (student, confidence, register)

def view(month, year, date):
    """
    This function returns a dataframe representing the attendance register for the specified date, month and year.
    """
    
    path = dbpath / f"{year}/{month}.csv"
    
    if not path.exists():
        raise Exception(f"No records available for {month} {year}")
        
    register = pd.read_csv(path)

    if date != "0":
        if date in register.columns:
            columns = ["roll", "name", date]
            register = register[columns]
            
        else:
            raise Exception(f"Attendance not availabe for this date: {date}")    

    register = register.set_index(register["roll"]).drop("roll", axis=1)
    return register

def percent(months, year):
    """
    Output: a tuple with two elements
    0. working_days = number of days school was open.
    1. df (dataframe) = a dataframe consisting of 4 columns:
        0. roll
        1. name
        2. total (number of days student's attendance was marked present in the specified range)
        3. % (number of days student attendance marked present * 100 / total number of working days)
    """
    
    df = pd.read_csv(metapath)
    df["Total"] = ""
    working_days = 0
                
    for month in months:
        path = dbpath / f"{year}/{month}.csv"
                    
        if not path.exists():
            continue
        
        register = pd.read_csv(path)

        #register.columns = (roll, names, date, date, date, ...)
        working_days += len(register.columns) - 2
                    
        for column in register.columns[2:]:
            df["Total"] += register[column]

    if working_days == 0:
        raise Exception("No attendance for the given month(s)")

    #students.loc[idx, "Total"] = "APAPPPAPAA..."
    #We can get total attendance for this student by counting number of 'P' (Present marking)

    for idx, row in enumerate(df["Total"]):
        df.loc[idx, "Total"] = str(row.count("P"))
        df.loc[idx, "%"] = f"{row.count('P') * 100 / working_days:.0f}%"
        
    df = df.set_index(df["roll"]).drop("roll", axis=1)
    return (working_days, df)
        
def remove(name, options):
    """
    Input:
        name (string) = option selected by user. For example, '1. Arush' or '4. Zoheb'
        options (list) = all available options
        
    Output:
        names (dataframe) = metadata dataframe with changes implemented. 
    """
    
    index_remove = options.index(name)
    
    names = pd.read_csv(metapath)
    names_length = len(names.index)
        
    names = names.drop(index_remove, axis=0)
    names.iloc[index_remove:, 0] -= 1
    names = names.set_index(range(names_length))
    names.to_csv(metapath)

    names = names.set_index(names["roll"]).drop("roll", axis=1)
    return names
    
def show_deleted(df, full_names):
    """
    Removing a student only changes the metadata, only the past attendance regusters in which the removed student's name is present.
    
    This function allows the user to see deleted students in past registers if they so desire.
    
    Input: 0. df (dataframe) = register in which changes are to be made. 1. full_names (tuple) = tuple of all names in metadata.csv in order
    Returns the register dataframe with changes made.
    """
    
    truth = []
    for idx in df.index:
        truth.append(df.loc[idx, "name"] in full_names)

    cleaned = df[truth]
    cleaned["roll"] = range(1, sum(truth) + 1)
    return cleaned
    
def order_months(year):
    """
    Attendance is stored as <month_name>.csv, lying in the appropriate <year_name> directory inside the 'database' directory. Reading month names directly causes them to be in alphabetical order, which is not ideal for the menu display.
    
    This function takes a list of month names (in alphabetical order) and returns a new list, with the month names in correct chronological order.
    """
    
    if not year:
        return None
                   
    path = dbpath / str(year)
    unordered_months = [month.stem for month in path.iterdir()]

    ordered_months = []
    for month in full_months:
        if month in unordered_months:
            ordered_months.append(month)

    return ordered_months
    
