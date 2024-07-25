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
from .serializers import UserSerializer,AttendanceSerializer,AttendanceSerializerWithUserDetails
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
from django.db.utils import IntegrityError
class AdminRegisterView(APIView):
    def post(self, request):
        data = request.data

        try:

            user = User(
                full_name=data['full_name'],
                username=data['username'],
                password=data['password'],
                is_superuser=True,
                smtp_email=data['smtp_email'],
                smtp_password=data['smtp_password']

            )

            user.save()
        except IntegrityError as e:
            return Response({"error_message": "User ID Already Exists!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Admin registered successfully"}, status=status.HTTP_201_CREATED)

class AdminLoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = get_object_or_404(User, username=username, password=password,is_superuser=True)
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class ChangeAdminSMDP(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_superuser:
            return Response({
                "message": 'You are not Authorized to change SMTP!',

            }, status=status.HTTP_403_FORBIDDEN)

        smtp_email = request.data['smtp_email']
        smtp_password = request.data['smtp_password']
        user.smtp_email = smtp_email
        user.smtp_password = smtp_password
        user.save()
        return Response({
            "message": 'SMTP Email and Password updated successfully.',

        }, status=status.HTTP_200_OK)

class AdminGetUsers(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            return Response({
                "message": 'You are not Authorized to get all Users!',

            }, status=status.HTTP_403_FORBIDDEN)
        return User.objects.filter(is_superuser=False)

class AdminGetTodaysAttendance(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializerWithUserDetails

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            return Response({
                "message": 'You are not Authorized to get attendance!',

            }, status=status.HTTP_403_FORBIDDEN)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        user_id = self.request.query_params.get('user_id', None)
        date_str = self.request.query_params.get('date', None)
        user_id = self.request.query_params.get('user_id', None)

        # Convert date_str to a datetime.date object
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    "message": "Invalid date format. Use YYYY-MM-DD.",
                }, status=status.HTTP_400_BAD_REQUEST)

            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())

            if user_id:
                return Attendance.objects.filter(
                    timestamp__range=(start_of_day, end_of_day),
                    user__university_id=user_id
                )
            else:
                return Attendance.objects.filter(
                    timestamp__range=(start_of_day, end_of_day)
                )
        else:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            if user_id:
                return Attendance.objects.filter(timestamp__gte=today, user__university_id=user_id)
            else:
                return Attendance.objects.filter(timestamp__gte=today)


def admin_view(request):
    if User.objects.filter(is_superuser=True).exists():
        return render(request, 'attendance/admin_login.html')
    else:
        return render(request, 'attendance/admin_register.html')

def admin_dashboard(request):
    # if not request.user.is_superuser:
    #     return redirect('home')
    # Your admin dashboard logic here
    return render(request, 'attendance/admin_dashboard.html')

def change_email_password(request):

    return render(request, 'attendance/change_email_password.html')
from .models import UserProfile
from .forms import AccountSettingsForm
from .forms import NotificationSettingsForm
from django.contrib.auth import get_user_model


def home(request):
    return render(request, 'attendance/home.html')

def about(request):
    return render(request, 'attendance/about.html')

def sign_in_view(request):

    form = AuthenticationForm()
    return render(request, 'attendance/SignIn.html', {'form': form})

def sign_up_view(request):
    # if request.method == 'POST':
    #     form = SignUpForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         login(request, user)
    #         messages.success(request, 'Account created successfully.')
    #         return redirect('profile')
    #     else:
    #         messages.error(request, 'Please correct the errors below.')
    # else:
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


def profile_view(request):
    return render(request, 'attendance/profile.html')


def attendance_view(request):
    return render(request, 'attendance/attend.html')

def settings_view(request):
    return render(request, 'attendance/settings.html')


def dashboard_view(request):
    return render(request, 'attendance/dashboard.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')

def weekly_attendance_view(request):
    return render(request, 'attendance/weekly_attendance.html')

def attendance_records(request):
    return render(request, 'attendance/attendance_records.html')



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
        try:

            user = User(
                full_name=data['full_name'],
                university_id=data['university_id'],
                password=data['password'],
                image_url=image_url,
            )
            user.set_face_encoding(face_encoding)
            user.save()
        except IntegrityError as e:
            return Response({"error_message": "User ID Already Exists!"}, status=status.HTTP_400_BAD_REQUEST)
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
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        return
    sender_email = user.smtp_email
    receiver_email = user.smtp_email
    password = user.smtp_password

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

def role_selection(request):
    # This view renders a page where users can choose their role
    return render(request, 'attendance/role_selection.html')

def sign_in_student(request):
    # Adapt this to handle student-specific sign-in logic or just render a template
    if request.method == 'POST':
        # Handle student login
        pass
    return render(request, 'attendance/sign_in_student.html')

def sign_in_admin(request):
    # Adapt this to handle admin-specific sign-in logic or just render a template
    if request.method == 'POST':
        # Handle admin login
        pass
    return render(request, 'attendance/sign_in_admin.html')

def sign_in_student(request):
    # Handle student-specific login logic or render a student template
    return render(request, 'attendance/sign_in_student.html')

def sign_in_employee(request):
    # Handle employee-specific login logic or render an employee template
    return render(request, 'attendance/sign_in_employee.html')


def add_view_groups(request):
    return render(request, 'attendance/add_view_groups.html')


def messages(request):
    return render(request, 'attendance/messages.html')

def app_settings(request):
    # Your view logic here
    return render(request, 'attendance/settings/app_settings.html')

def calendar(request):
    return render(request, 'attendance/calendar.html')


def activity(request):
    return render(request, 'attendance/activity.html')

def users(request):
    return render(request, 'attendance/users.html')
def smtp_settings(request):
    return render(request, 'attendance/smtp_settings.html')

def admin_user_attendance(request):
    return render(request, 'attendance/admin_user_attendance.html')

def overall_attendance(request):
    return render(request, 'attendance/overall_attendance.html')

def mark_attendance(request):
    return render(request, 'attendance/mark_attendance.html')

def account_settings(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AccountSettingsForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your account settings have been updated successfully.')
                return redirect('account_settings')
        else:
            form = AccountSettingsForm(instance=request.user)
    else:
        # Handle anonymous users or provide a dummy form
        form = AccountSettingsForm()  # Could be a blank form or customized for anonymous users

    return render(request, 'attendance/settings/account.html', {'form': form})

def notifications(request):
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data
            # Here you would save the data to your database or user session
            return redirect('notification_settings')  # Redirect to the same page to show a fresh form
    else:
        form = NotificationSettingsForm()  # An unbound form

    return render(request, 'attendance/settings/notifications.html', {'form': form})
def password_reset(request):
    if request.method == 'POST':
        # Handle POST request
        pass
    return render(request, 'attendance/settings/password_reset.html')

def privacy_settings(request):
    # Handle privacy related settings here
    return render(request, 'attendance/settings/privacy_settings.html')

def contact_support(request):
    # Handle support contact logic here
    return render(request, 'attendance/settings/support.html')


def privacy_settings(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Get form data
            profile_visibility = request.POST.get('profile_visibility')
            email_notifications = 'email_notifications' in request.POST
            data_sharing = 'data_sharing' in request.POST
            activity_tracking = 'activity_tracking' in request.POST
            
            # Get the current user's profile or create one if it doesn't exist
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Update the user's profile settings
            user_profile.profile_visibility = profile_visibility
            user_profile.email_notifications = email_notifications
            user_profile.data_sharing = data_sharing
            user_profile.activity_tracking = activity_tracking
            user_profile.save()
            
            # Optionally add a success message
            messages.success(request, 'Your privacy settings have been updated successfully.')
            
            # Redirect back to the settings page
            return redirect('settings')
        else:
            # Handle the case where the user is not authenticated
            messages.error(request, 'You need to be logged in to update privacy settings.')
            return redirect('login')  # Redirect to login page or wherever appropriate

    # Provide context for the initial form render
    context = {
        # Add necessary context if needed
    }
    return render(request, 'attendance/settings/privacy_settings.html', context)

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            if UserProfile.objects.filter(email=email).exists():
                user_profile = UserProfile.objects.get(email=email)
                user = user_profile.user
                # Implement password reset logic here
                return HttpResponse("Password reset link has been sent to your email.")
            else:
                return HttpResponse("No user with that email found.")
        except UserProfile.DoesNotExist:
            return HttpResponse("No user with that email found.")
    return render(request, 'attendance/settings/forgot_password.html')

def reset_password_code(request):
    if request.method == 'POST':
        email = request.POST['email']
        reset_code = request.POST['reset_code']
        user = User.objects.get(email=email)
        if user.profile.reset_code == int(reset_code):
            return redirect('set_new_password')
        else:
            messages.error(request, 'Invalid reset code')
    return render(request, 'attendance/settings/reset_password_code.html')

def set_new_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('sign_in')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'attendance/settings/set_new_password.html')

scheduler = BackgroundScheduler()
#Use this for testing
scheduler.add_job(send_attendance_email, 'interval', minutes=20)
#Use this to make it send at hour 17
# scheduler.add_job(send_attendance_email, 'cron', hour=17, minute=0)
send_attendance_email()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

