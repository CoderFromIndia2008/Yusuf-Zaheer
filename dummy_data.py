import pathlib as pt
import random as rn
import pandas as pd
import datetime

data = {
    "roll": (1,2,3,4,5,6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22),
    "name": ("Aryan", "Arush", "Jaffar", "Krishna", "Yusuf", "Zoheb", "Nasir", "Archit", "Siddhanto", "Mansi", "Tejas", "Prabhat", "Vinayak", "Atulya", "Saksham", "Yashi", "Vedant", "Akansha", "Aditya", "Hashir", "Samarth", "Hasan")
    }

meta = pd.DataFrame(data)
print("hello")
years = 24, 25, 26
month_length = {
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31,
    "January": 31,
    "February": 28,
    "March": 31
}

for year in years:
    path = pt.Path.cwd() / "database" / f"20{year}-{year+1}"

    for idx, month in enumerate(month_length.keys()):
        register = data.copy()
        for day in range(1, month_length[month] + 1):
            date = datetime.date(2000+year, month, day)
            weekday = date.strftime("%a")

            l = []
            for j in range(22):
                l.append(rn.choices(["P", "A"], [75, 25])[0])                                
            register[f"{day}\n{weekday}"] = l

        df = pd.DataFrame(register)
        path.mkdir(exist_ok = True)
        df.to_csv(path / f"{idx+1}_{month}_20{year}-{year+1}.csv", index=False)
        meta.to_csv(path / f"metadata_20{year}-{year+1}.csv", index=False)

