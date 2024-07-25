from rest_framework import serializers
from .models import User
from .models import Attendance
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'university_id','image_url','last_login',]

        extra_kwargs = {
            'password': {'write_only': True}
        }


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['user', 'timestamp']

class AttendanceSerializerWithUserDetails(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Attendance
        fields = ['user', 'timestamp']