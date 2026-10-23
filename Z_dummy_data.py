import pathlib as pt
import random as rn
import pandas as pd

data = {
    "roll": (1,2,3,4,5,6),
    "name": ("Aryan", "Arush", "Jaffar", "Krishna", "Yusuf", "Zoheb")
    }

meta = pd.DataFrame(data)

year = 25
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
    "February": 29 if year%4==0 or (year%400==0 and year%100 != 0) else 28,
    "March": 31
}

path = pt.Path(f"/workspaces/Yusuf-Zaheer/database/20{year}-{year+1}")

for idx, month in enumerate(month_length.keys()):
    register = data.copy()
    for i in range(1, month_length[month] + 1):
        l = []
        for j in range(6):
            attendance = rn.randint(0,1)
        
            if attendance == 0:
                l.append("A")
            
            else:
                l.append("P")
            
        register[i] = tuple(l)

    df = pd.DataFrame(register)
    path.mkdir(exist_ok = True)
    df.to_csv(path / f"{idx+1}_{month}_20{year}-{year+1}.csv", index=False)
    meta.to_csv(path / f"metadata_20{year}-{year+1}.csv", index=False)

