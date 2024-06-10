from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from django.http import HttpResponse
from django.http import JsonResponse
import dlib
import cv2 
import numpy as np
import csv
import os
from datetime import datetime


def home(request):
    return render(request, 'attendance/home.html')

def about(request):
    return render(request, 'attendance/about.html')

def sign_in_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully signed in!')
                return redirect('profile')  # Redirect to profile page
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'attendance/SignIn.html', {'form': form})

def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user
            messages.success(request, 'Account created successfully.')
            return redirect('profile')  # Redirect to profile page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'attendance/SignUp.html', {'form': form})

def submit_attendance(request):
    if request.method == 'POST':
        # Process the submitted data here
        name = request.POST.get('name')
        date = request.POST.get('date')
        # Implement the logic to handle the attendance record
        return HttpResponse(f"Attendance submitted for {name} on {date}")
    return render(request, 'attendance/submit_attendance.html')

def facial_recognition(request):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    face_rec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

    faceScanner = cv2.VideoCapture(0)

    known_faces = []
    known_names = []

    # Load known faces and names
    img_directory = "Pictures"
    for filename in os.listdir(img_directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(img_directory, filename)
            image = cv2.imread(img_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            dets = detector(rgb_image)
            for det in dets:
                shape = predictor(rgb_image, det)
                face_descriptor = face_rec.compute_face_descriptor(rgb_image, shape)
                known_faces.append(np.array(face_descriptor))
                known_names.append(os.path.splitext(filename)[0])

    entries = known_names.copy()
    face_names = []

    while True:
        ret, frame = faceScanner.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        dets = detector(rgb_frame)
        for det in dets:
            shape = predictor(rgb_frame, det)
            face_descriptor = face_rec.compute_face_descriptor(rgb_frame, shape)
            face_distances = np.linalg.norm(np.array(known_faces) - face_descriptor, axis=1)
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] < 0.6:  # Threshold for similarity
                name = known_names[best_match_index]
                face_names.append(name)
                if name in entries:
                    entries.remove(name)
                    currentTime = datetime.now().strftime("%H:%M:%S")
                    # Write to CSV or database
                    print(f"Attendance recorded for {name} at {currentTime}")

        cv2.imshow('Facial Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    faceScanner.release()
    cv2.destroyAllWindows()

    return JsonResponse({"status": "success", "recognized_faces": face_names})

@login_required
def profile_view(request):
    return render(request, 'attendance/profile.html')

@login_required
def attendance_view(request):
    return render(request, 'attendance/attendance.html')

@login_required
def settings_view(request):
    return render(request, 'attendance/settings.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')
