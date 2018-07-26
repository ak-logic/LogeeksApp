from django.db import models
import datetime
from django.utils import timezone

# Create your models here.


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=10, primary_key=True)
    date_initialized = models.DateField(verbose_name='Initialization Date', default=timezone.now)
    student_id = models.CharField(max_length=10, null=True, editable=False)
    tutor_number = models.CharField(max_length=10, editable=False)
    total_amount_due = models.FloatField(editable=False)
    payment_status = models.BooleanField(default=False)
    num_of_days_per_week = models.IntegerField()
    hours_per_day = models.IntegerField()
    validated = models.BooleanField(default=False)
    report_tutor = models.BooleanField(default=False)
    blacklist_student = models.BooleanField(default=False)
    tutor_notified = models.BooleanField(default=False)
    student_notified = models.BooleanField(default=False)
    tutor_payment = models.FloatField(editable=False, blank=False)

    def __str__(self):
        return str(self.transaction_id) + ' - between Student ' + str(self.student_id) + ' and Tutor ' + str(self.tutor_number)

    class Meta:
        ordering = ["-date_initialized"]


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    related_transaction = models.CharField(max_length=10)
    student_id = models.CharField(max_length=5, blank=True)
    tutor_number = models.CharField(max_length=7, blank=True)
    title = models.CharField(max_length=50)
    message_for_tutor = models.CharField(max_length=300, blank=True)
    message_for_student = models.CharField(max_length=300, blank=True)
    read_status = models.BooleanField(default=False)
    other_info = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return 'Notification ' + str(self.notification_id)

    class Meta:
        ordering = ["date"]


class Payroll(models.Model):
    tutor_number = models.CharField(max_length=7)
    tutor_name = models.CharField(max_length=80)
    transaction = models.CharField(max_length=10)
    tutor_bank_account_name = models.CharField(max_length=80, verbose_name='Tutor Account Name', blank=False)
    tutor_bank_account_number = models.CharField(max_length=10, verbose_name='Tutor NUBAN', blank=False)
    payment_date = models.DateField()
