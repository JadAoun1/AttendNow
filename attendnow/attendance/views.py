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
    # Ensure the paths are correct relative to your project directory
    predictor_path = "attendnow/attendnow/shape_predictor_68_face_landmarks.dat"
    face_rec_model_path = "attendnow/attendnow/dlib_face_recognition_resnet_model_v1.dat"

    try:
        predictor = dlib.shape_predictor(predictor_path)
        face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)
    except Exception as e:
        return HttpResponse(f"Error loading models: {str(e)}")

    # Your facial recognition code here
    return HttpResponse("Facial recognition logic executed successfully.")

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
