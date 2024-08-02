from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_age(value):
    if value and (timezone.now().date() - value).days < 18 * 365:
        raise ValidationError("You must be at least 18 years old to register.")

class CustomUserManager(BaseUserManager):
    def create_user(self, username, fullname, email, dob, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            fullname=fullname,
            email=self.normalize_email(email),
            dob=dob,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, fullname, email, dob, password=None):
        user = self.create_user(
            username,
            fullname,
            email,
            dob,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    dob = models.DateField(validators=[validate_age])
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['fullname', 'email', 'dob']

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin
