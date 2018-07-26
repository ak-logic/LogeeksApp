from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
from image_cropping import ImageCropField, ImageRatioField

from django.db import models
from location_field.models.plain import PlainLocationField


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=25, blank=True)
    gender = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=18, blank=True)
    home_address = models.CharField(max_length=90, blank=True)
    photo = ImageCropField(upload_to='media/student/', editable=True, blank=True)
    cropping = ImageRatioField('photo', '260x260', hide_image_field=True)
    email_verification = models.BooleanField(default=False)
    account_activation_status = models.BooleanField(default=False)
    num_of_times_blacklisted = models.PositiveIntegerField(default=0)
    choice_color = models.CharField(max_length=30, default='#6598b3')
    diary = models.CharField(max_length=1000, blank=True)
    city = models.CharField(max_length=255)
    location = PlainLocationField(based_fields=['city'], zoom=7)


    def __str__(self):
        return "Student " + str(self.id)

