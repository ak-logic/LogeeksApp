from django.db import models
# from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User
from django.utils import timezone
from image_cropping import ImageCropField, ImageRatioField


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # TODO: store the Subjects (key/value pair) in the subjects_offered.txt in the homepage static folder rather than
    # TODO: storing such delicate (and dynamic) info in different parts of the different apps in the Project.
    # TODO: Then collect and store the data into the subject_list by using the python 'open' and 'file.read_line' keywords.

    subject_list = (('Mathematics', 'Mathematics'), ('English', 'English Language'), ('Biology', 'Biology'),
               ('Physics', 'Physics'), ('Chemistry', 'Chemistry'), ('Further Maths', 'Further Maths'),
               ('Computer Studies', 'Computer Studies'), ('Technical Drawing', 'Technical Drawing'))

    # TODO: store the Lagos LGAs (key/value pair) in the local_gov_areas_in_lagos.txt in the homepage static folder
    # TODO: rather than storing such delicate (and dynamic) info in different parts of the different apps in the Project.
    # TODO: Then collect and store the data into the nigeria_lagos_lga by using the python 'open' and 'file.read_line' keywords.

    nigeria_lagos_lga = (
        ('apapa', 'apapa'), ('ajah', 'ajah'), ('bariga', 'bariga'), ('ebute-meta', 'ebute-meta'),
        ('eti-osa', 'eti-osa'), ('festac', 'festac'), ('gbagada', 'gbagada'), ('ibeju-lekki', 'ibeju-lekki'),
        ('ifako-ijaye', 'ifako-ijaye'), ('ikeja', 'ikeja'), ('ikorodu', 'ikorodu'),
        ('ikoyi-obalende', 'ikoyi-obalende'),
        ('ilupeju', 'ilupeju'), ('ketu', 'ketu'), ('kosofe', 'kosofe'), ('lagos-island', 'lagos-island'),
        ('lagos-mainland', 'lagos-mainland'), ('magodo', 'magodo'), ('onipanu', 'onipanu'),
        ('oshodi-isolo', 'oshodi-isolo'), ('somolu', 'somolu'), ('surulere', 'surulere'),
        ('victoria-island', 'victoria-island')
    )
    states_in_nigeria = (('lagos', 'lagos'), ('others', 'others'))
    country = models.CharField(max_length=100, default='Nigeria')
    state = models.CharField(max_length=100, choices=states_in_nigeria, default="Lagos, Nigeria")
    lga1 = models.CharField(max_length=100, choices=nigeria_lagos_lga, default='Invalid_lga')
    lga2 = models.CharField(max_length=100, choices=nigeria_lagos_lga, default='Invalid_lga')
    lga3 = models.CharField(max_length=100, choices=nigeria_lagos_lga, default='Invalid_lga')
    # lga_tuple = (lga1, lga2, lga3)
    TUTOR_GENDER = (('Male', 'Male'), ('Female', 'Female'))
    subject = models.CharField(max_length=20, choices=subject_list)
    gender = models.CharField(max_length=6, choices=TUTOR_GENDER, default="Gender")
    middle_name = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=18)
    address = models.CharField(max_length=200)
    qualification = models.FloatField(default=0)
    recommendation = models.FloatField(default=2.5)
    rating = models.FloatField(default=0.0)
    charge = models.FloatField(default=0.0)
    photo = ImageCropField(upload_to='media/tutor/', editable=True, blank=True)
    cropping = ImageRatioField('photo', '260x260')
    availability = models.PositiveSmallIntegerField(verbose_name="Tutor's Availability", default=2)
    is_visible = models.BooleanField(default=True)
    experience = models.PositiveSmallIntegerField(default=0)
    bank_account_name = models.CharField(max_length=80)
    bank_account_number = models.CharField(max_length=10)
    # proficiency_level =

    def __str__(self):
        return "Tutor: " + str(self.user.username)


class TutorNotification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    related_transaction = models.CharField(max_length=10)
    message_title = models.CharField(max_length=50)
    message_content = models.CharField(max_length=1000)
    read_status = models.BooleanField(default=False)
    notification_tag = models.CharField(max_length=20)

    def __str__(self):
        return self.notification_id
