#run this file to add new data to database
#manually add new data down below

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-63e7b-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "111":
        {
            "Name": "Biswajit Chatterjee",
            "Subject": "Professor in Law",
            "Starting_Year": 1990,
            "Total_Attendance": 10,
            "Grade": "A+",
            "Year": 4,
            "last_attendance_time": "2024-09-09 00:54:34"

        },
    "222":
        {
            "Name": "Aranya Chatterjee",
            "Subject": "AI/ML",
            "Starting_Year": 2024,
            "Total_Attendance": 15,
            "Grade": "A+",
            "Year": 2,
            "last_attendance_time": "2024-09-09 00:54:34"

        },
    "3333":
        {
            "Name": "Mou Saha",
            "Subject": "Data Analytics",
            "Starting_Year": 2024,
            "Total_Attendance": 1,
            "Grade": "A",
            "Year": 1,
            "last_attendance_time": "2024-09-09 00:54:34"

        },
    "9635":
        {
            "Name": "Pranojjal Roy",
            "Subject": "Networking",
            "Starting_Year": 2024,
            "Total_Attendance": 1,
            "Grade": "C",
            "Year": 4,
            "last_attendance_time": "2024-09-09 00:54:34"

        },
    "181118":
        {
            "Name": "Arna Chatterjee",
            "Subject": "Alphabets",
            "Starting_Year": 2024,
            "Total_Attendance": 2,
            "Grade": "A+",
            "Year": 1,
            "last_attendance_time": "2024-09-09 00:54:34"

        },
}

for key, value in data.items():
    ref.child(key).set(value)
print("Data Successfully Uploaded to database")