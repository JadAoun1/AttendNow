from django.shortcuts import render

def home(request):
    return render(request, 'attendance/home.html')

def about(request):
    return render(request, 'attendance/about.html')

def profile(request):
    return render(request, 'attendance/profile.html')

def signin(request):
    return render(request, 'attendance/signin.html')

def signup(request):
    return render(request, 'attendance/signup.html')

def logout(request):
    # Handle logout logic here
    pass
