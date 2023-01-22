from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, first_name, password, **other_fields)

    def create_user(self, email, user_name, first_name,  company, mobile_number, password, **other_fields):

        other_fields.setdefault('is_active', True)

        if not email:
            raise ValueError(('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, first_name=first_name, 
                        company=company, mobile_number=mobile_number, password=password, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Newuser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(('email address'), unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    mobile_number = models.CharField(max_length=10)
    company = models.CharField(max_length=5)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name', 'mobile_number']

    def __str__(self):
        return self.user_name


class Todo(models.Model):
    title = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    car_type = models.CharField(max_length=150, default='')
    memo = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(Newuser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_name