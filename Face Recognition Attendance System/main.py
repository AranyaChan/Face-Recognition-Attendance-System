from datetime import datetime
import time

import cv2
import os
import pickle
import cvzone
import face_recognition
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-63e7b-default-rtdb.firebaseio.com/",
    'storageBucket':"face-recognition-attenda-63e7b.appspot.com"
})


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/Background.png')


# importing mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList =[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))


#importing/loading the encoding file
print("Loading Encoded file...")
file = open('encodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encoded file Loaded Successfully")


bucket = storage.bucket()
modeType=0
counter=0
id = -1
imgStudent = []



while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # from BGR(used by openCV) to RGB(used by face recognition library)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)


    # binding the background, modes and the cam
    imgBackground[162:162+480,55:55+640]= img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print("matches", matches)
            #print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            #print("matchIndex", matchIndex)

            if matches[matchIndex]:
                #print("Known Face detected", studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4 #multiplying by 4 as the cam size is reduced by 4 times above
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox,colorR=(0,0,255), rt=0)
                #imgBackground = cv2.rectangle(imgBackground,bbox, color=(0,0,255))

                id = studentIds[matchIndex] #id of matched Student
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275,400))
                    cv2.imshow("Face Recognition", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1


        if counter!=0:

            if counter == 1:

                #getting the data from the database
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #getting the Student Image from the Storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8) #code for converting the image, np.uint8 means numpy unsigned integer 8 bits
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                #last attendance time
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S") #string to object
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()


                if secondsElapsed > 30:
                    #Updating the data of the Attendance
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_Attendance'] += 1
                    ref.child('Total_Attendance').set(studentInfo['Total_Attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))#last attendance time, object to string
                else:
                    #already marked
                    modeType=3
                    counter=0
                    seconds=30
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    cv2.putText(imgBackground, "Can be marked again after 30 seconds", (825, 625), cv2.FONT_HERSHEY_DUPLEX, .6, (100, 100, 100), 1)
            if modeType !=3:

                if 10< counter <=20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <=10:
                    #displaying all Student info
                    cv2.putText(imgBackground, str(studentInfo['Total_Attendance']),(861,125), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['Subject']),(1006,550), cv2.FONT_HERSHEY_DUPLEX, .5, (255,255,255),1)
                    cv2.putText(imgBackground, str(id),(1006,493), cv2.FONT_HERSHEY_DUPLEX, .5, (255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['Grade']),(910,625), cv2.FONT_HERSHEY_DUPLEX, .6, (100,100,100),1)
                    cv2.putText(imgBackground, str(studentInfo['Year']),(1025,625), cv2.FONT_HERSHEY_DUPLEX, .6, (100,100,100),1)
                    cv2.putText(imgBackground, str(studentInfo['Starting_Year']),(1125,625), cv2.FONT_HERSHEY_DUPLEX, .6, (100,100,100),1)

                    #adjusting the size of the Name to fit properly and displaying it
                    (w,h), _ = cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_DUPLEX,1,1)
                    offset = (414 - w)//2
                    cv2.putText(imgBackground, str(studentInfo['Name']),(808+offset,445), cv2.FONT_HERSHEY_DUPLEX, 1, (50,50,50),1)

                    #displaying the image
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter+=1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo=[]
                    imgStudent = []

    else:
        counter=0
        modeType=0
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow("Face Recognition", imgBackground)
    cv2.waitKey(1)
