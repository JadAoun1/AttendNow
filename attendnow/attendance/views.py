# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import SignUpForm, SignInForm

def home(request):
    return render(request, 'attendance/home.html')

def about(request):
    return render(request, 'attendance/about.html')

def sign_in_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully signed in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = SignInForm()
    return render(request, 'attendance/signIn.html', {'form': form})

def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now sign in.')
            return redirect('signin')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'attendance/signUp.html', {'form': form})

def profile_view(request):
    # Add your profile view logic here
    return render(request, 'attendance/profile.html')

def attendance_view(request):
    # Add your attendance view logic here
    return render(request, 'attendance/attendance.html')

def settings_view(request):
    # Add your settings view logic here
    return render(request, 'attendance/settings.html')
