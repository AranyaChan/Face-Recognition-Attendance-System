#run this encode file when new students are added

import pickle
import cv2
import face_recognition
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-63e7b-default-rtdb.firebaseio.com/",
    'storageBucket':"face-recognition-attenda-63e7b.appspot.com"
})



# importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)

imgList =[] # stores the images of the students
#print(pathList)
studentIds = [] # stores IDs of all the students


for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    #sending the image files to firebase storage
    fileName=f'{folderPath}/{path}' #going as "Images" folder, used python f string here
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

#print(studentIds)


def findEncodings(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #from BGR(used by openCV) to RGB(used by face recognition library)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        #print(encode)
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,studentIds]
print("Encoding Complete!")

file = open("EncodeFile.p", 'wb') #wb is permission, writing in binary wb
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
