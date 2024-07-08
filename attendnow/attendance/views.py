from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm
from django.http import HttpResponse
import dlib
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.generics import ListAPIView
from datetime import timedelta
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User,Attendance
from .serializers import UserSerializer,AttendanceSerializer
from django.conf import settings
import face_recognition
import boto3
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cv2
from datetime import datetime
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
def home(request):
    return render(request, 'attendance/home.html')

def about(request):
    return render(request, 'attendance/about.html')

def sign_in_view(request):

    form = AuthenticationForm()
    return render(request, 'attendance/SignIn.html', {'form': form})

def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'attendance/signUp.html', {'form': form})

def submit_attendance(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        return HttpResponse(f"Attendance submitted for {name} on {date}")
    return render(request, 'attendance/submit_attendance.html')

def facial_recognition(request):
    predictor_path = "attendnow/attendnow/shape_predictor_68_face_landmarks.dat"
    face_rec_model_path = "attendnow/attendnow/dlib_face_recognition_resnet_model_v1.dat"

    try:
        predictor = dlib.shape_predictor(predictor_path)
        face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)
    except Exception as e:
        return HttpResponse(f"Error loading models: {str(e)}")

    return HttpResponse("Facial recognition logic executed successfully.")


def home_view(request):
    return render(request, 'attendance/home.html')

@login_required
def profile_view(request):
    return render(request, 'attendance/profile.html')


def attendance_view(request):
    return render(request, 'attendance/attend.html')

@login_required
def settings_view(request):
    return render(request, 'attendance/settings.html')

@login_required
def dashboard_view(request):
    return render(request, 'attendance/dashboard.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')

def weekly_attendance_view(request):
    return render(request, 'attendance/weekly_attendance.html')



s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name=settings.AWS_S3_REGION_NAME)


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        file = data['photo']
        path = default_storage.save('tmp/' + file.name, ContentFile(file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        s3.upload_file(tmp_file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file.name}"

        image = face_recognition.load_image_file(tmp_file)
        face_encoding = face_recognition.face_encodings(image)[0]

        user = User(
            full_name=data['full_name'],
            university_id=data['university_id'],
            password=data['password'],
            image_url=image_url,
        )
        user.set_face_encoding(face_encoding)
        user.save()

        os.remove(tmp_file)

        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        university_id = request.data['university_id']
        password = request.data['password']

        user = get_object_or_404(User, university_id=university_id, password=password)
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)



class AttendView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        file = request.FILES['photo']
        path = default_storage.save('tmp/' + file.name, ContentFile(file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        image = face_recognition.load_image_file(tmp_file)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            os.remove(tmp_file)
            return Response({"message": "No faces detected in the image"}, status=status.HTTP_400_BAD_REQUEST)

        user_encoding = user.get_face_encoding()
        matched = False

        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([user_encoding], face_encoding)
            if match[0]:
                matched = True
                break

        if matched:
            filename = f'{datetime.now().strftime("%Y-%m-%d")}.csv'
            with open(filename, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([user.full_name, datetime.now().strftime("%H:%M:%S")])
            # Save attendance record
            Attendance.objects.create(user=user)

            os.remove(tmp_file)
            return Response({"message": f"Attendance recorded for {user.full_name}"}, status=status.HTTP_200_OK)
        else:
            os.remove(tmp_file)
            return Response({"message": "Your face was not recognized in the image"}, status=status.HTTP_401_UNAUTHORIZED)
class WeeklyAttendanceView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        one_week_ago = timezone.now() - timedelta(days=7)
        return Attendance.objects.filter(user=user, timestamp__gte=one_week_ago)

def send_attendance_email():
    sender_email = "<YOUR EMAIL>"
    receiver_email = "<RECEIVER EMAIL>"
    password = "<YOUR PASSWORD>"

    subject = "Attendance for Today's Class"
    body = "Hello! Here is the attendance of the class for today."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    filename = f'{datetime.now().strftime("%Y-%m-%d")}.csv'
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")

    msg.attach(part)
    text = msg.as_string()

    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)




scheduler = BackgroundScheduler()
#Use this for testing
# scheduler.add_job(send_attendance_email, 'interval', minutes=2)
#Use this to make it send at hour 17
# scheduler.add_job(send_attendance_email, 'cron', hour=17, minute=0)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

