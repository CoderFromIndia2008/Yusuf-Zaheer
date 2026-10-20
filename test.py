import pickle
with open("/workspaces/Yusuf-Zaheer/tools/password.dat", "wb") as f:
    data = pickle.dump([123], f);print(data)