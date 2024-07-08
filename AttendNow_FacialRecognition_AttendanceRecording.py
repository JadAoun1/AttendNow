#                                                                                                               #
# Prototype 2: Facial recognition, attendance recording, and video recording software for AttendNow             #   
# Created by Gavin Middleton                                                                                    #
#                                                                                                               #
# All the packages needed to be downloaded for the facial recognition software, this includes face_recognition  #
# opencv-python, cmake, and dlib for python version 3.9.                                                        #
#                                                                                                               #
# cmd >> "pip install cmake==3.25.2" >> "pip install dlib==19.24.2" >> "pip install face_recognition" >>        #
# "pip install openCV-python"                                                                                   #
#                                                                                                               #



import face_recognition
import cv2 as cam
import numpy as np
import csv
import os
from datetime import datetime

# This is opening the camera
faceScanner = cam.VideoCapture(0)
# - Show the current date in the excel spread sheet for when the student/employee clocks into work/class
timeNow = datetime.now()
currentDate = timeNow.strftime("%Y-%m-%d")

# Checks to see if the camera can be opened or not.
if not faceScanner.isOpened():
    print('Cannot open system camera.')
    exit(0)

# directory to the stored images, and new folder "Videos"
img_directory = "Pictures"
vid_directory = "Videos"

if not os.path.exists(vid_directory):
    os.makedirs(vid_directory)

# Recording, and file naming for the video recording
fourcc = cam.VideoWriter_fourcc(*'XVID')
RecOut = cam.VideoWriter(os.path.join(vid_directory, f'output_{currentDate}.avi'), fourcc, 20.0, (640, 480))

# lists to store the encoded pictures and the names of the students/employees
known_faces_names = []
known_face_encoding = []

# loading the images and creating encodings
for filename in os.listdir(img_directory):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(img_directory, filename)
        image = cam.load_image_file(img_path)
        # get face encoding
        try:
            encoding = face_recognition.face_encodings(image)[0]
        except IndexError:
            print(f"No faces found in {filename}. Skipping this file.")
            continue
        
        # extracting the name from the file
        name = os.path.splitext(filename)[0]
        
        # add encoding and name to the lists
        known_face_encoding.append(encoding)
        known_faces_names.append(name)

# copy all the names to the entries list        
entries = known_faces_names.copy()

# variables declared that are for the faces coming from the webcam
# - Face coordinates from the webcam
face_coords = []

# - Raw data
face_encoding = []

# - Name of the face, if present in the camera
face_names = []
trueVar = True

# - Parameters are as follows; file name ('2024-6-3.csv'), opening with write+ method, and newline has no value
attendanceList = open(currentDate + '.csv',  'w+', newline = '')

# - Class instance for writing data in the csv file
lnwriter = csv.writer(attendanceList)

while True:
    ret, frame = faceScanner.read()
    if not ret:
        print('Cannot recieve frame.\nExiting...')
        break
    
    small_frame = cam.resize(frame, (0, 0), fx = 0.25, fy = 0.25)
    rgb_small_frame = small_frame [:, :, :: - 1]
    
    # This will detect if there is a face in the frame or not
    face_coords = face_recognition.face_locations(rgb_small_frame)
        
    # Stores the face data of the face in the frame
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_coords)
    face_names = []
        
    for face_encoding in face_encodings:
            
        matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
        name = ""
        face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
            
        # numpy.argmin to get the best match from the data given in the webcam, and the database of pictures
        best_match_index = np.argmin(face_distance)
            
        # Then if the match exists the name will be connected with the face scan
        if matches[best_match_index]:
                
            name = known_faces_names[best_match_index]
                
                
        # Now we can enter the name in the csv file
        # if the appended name is in the known_faces_names list then we can write the name, and
        # time of attendance to the .csv file
            
        face_names.append(name)
        if name in known_faces_names:
            if name in entries:
                # The name is removed to prevent repetition
                # Write the entries in the .csv file and return that file to the database
                entries.remove(name)
                print("entries:", entries)
                currentTime = timeNow.strftime("%H:%M:%S")
                lnwriter.writerow([name, currentTime])
                    
    RecOut.write(frame)
        
    # This is the frame around the users face in the frame of the webcam
    for (top, right, bottom, left), name in zip(face_coords, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cam.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cam.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cam.FILLED)
        cam.putText(frame, name, (left + 6, bottom - 6), cam.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
  
    cam.imshow('Attendance System', frame)
    # Executed when 'q' is pressed
    if cam.waitKey(1) & 0xFF == ord('q'):
        break
    
faceScanner.release()
cam.destroyAllWindows()
attendanceList.close()