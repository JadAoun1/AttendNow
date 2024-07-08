from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import pickle


class UserManager(BaseUserManager):
    def create_user(self, university_id, password=None, **extra_fields):
        if not university_id:
            raise ValueError('The University ID field must be set')
        user = self.model(university_id=university_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, university_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(university_id, password, **extra_fields)

class User(AbstractBaseUser):
    full_name = models.CharField(max_length=100)
    university_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)
    face_encoding = models.BinaryField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'university_id'
    REQUIRED_FIELDS = ['full_name']

    def set_face_encoding(self, encoding):
        self.face_encoding = pickle.dumps(encoding)

    def get_face_encoding(self):
        return pickle.loads(self.face_encoding)

    def __str__(self):
        return self.university_id