import re, random
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, send_mass_mail
from django.contrib.auth.models import User
import datetime
from tutor.views import calculate_tutor_charge_per_hour
from django.utils import timezone
from tutor.models import Tutor
from student.models import Student
from transaction.models import Transaction, Notification
from django.contrib.auth.models import Permission
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth import views
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator


def format_currency(amount):
    """
    :param amount: the amount to be converted (a float)
    :return: the properly formatted amount (including commas where necessary)
    """
    amount = float(amount)
    stringed_amount = str(amount)
    kobo_denomination = stringed_amount[stringed_amount.index('.') + 1: ]
    naira_denomination = stringed_amount[:stringed_amount.index('.')]
    length_of_naira_denomination = len(naira_denomination)
    if length_of_naira_denomination <= 3:
        return stringed_amount
    elif 0 < length_of_naira_denomination % 3 < 3:
        first_part = naira_denomination[:(length_of_naira_denomination % 3)]
        second_part = naira_denomination[(length_of_naira_denomination % 3):]
    elif length_of_naira_denomination % 3 == 0:
        first_part = naira_denomination[:3]
        second_part = naira_denomination[3:]
    properly_formatted_naira = first_part

    while len(second_part) > 0:
        properly_formatted_naira += ',' + second_part[:3]
        second_part = second_part[3:]
    return properly_formatted_naira + '.' + kobo_denomination


# @login_required(login_url='/student/sign_in/', redirect_field_name='next')
def initialize_transaction(request):
    if request.method=='POST':
        hired_tutor_number = request.POST['hired_tutor_number']
        hired_tutor_user = User.objects.get(username=hired_tutor_number)
        hired_tutor = hired_tutor_user.tutor
        hired_tutor.charge = calculate_tutor_charge_per_hour(hired_tutor.experience, hired_tutor.rating,
                                                             hired_tutor.recommendation,hired_tutor.qualification)
        hired_tutor.save()
        context = {'hired_tutor': hired_tutor, 'tutor_charge_per_hour': format_currency(hired_tutor.charge), 'hired_tutor_number': hired_tutor_number, 'hired_tutor_user': hired_tutor_user}
        return render(request, 'transaction/initialize_transaction.html', context)
    return redirect('/student/select_tutor/')


# @login_required(login_url='/student/sign_in/', redirect_field_name='next')
def confirm_transaction(request):
    if request.method == 'POST':
        hired_tutor_number = request.POST['hired_tutor_number']
        num_of_days_per_week = request.POST['num_of_days_per_week']
        num_of_hours_per_day = request.POST['num_of_hours_per_day']
        tutor_user = User.objects.get(username=hired_tutor_number)
        tutor = tutor_user.tutor
        tutor.charge = calculate_tutor_charge_per_hour(tutor.experience, tutor.rating, tutor.recommendation,
                        tutor.qualification)
        tutor.save()
        transport_fare_per_day = 500.0
        num_of_weeks_in_a_month = 4
        total_tuition = (float(num_of_days_per_week) * float(num_of_hours_per_day) * num_of_weeks_in_a_month) * \
                        tutor.charge
        total_transport_fare = transport_fare_per_day * float(num_of_days_per_week) * float(num_of_weeks_in_a_month)
        total_amount_due = total_tuition + total_transport_fare
        tutor_payment_percentage = 0.75
        tutor_payment = tutor_payment_percentage * total_tuition
        tutor_total_payment_and_transport_allowance = tutor_payment + total_transport_fare

        student_id = None
        try:
            if (request.user.student):
                student_id = request.user.username
        except Exception as e:
            pass

        def generate_transaction_id():
            day = str(timezone.now().day) if (len(str(timezone.now().day)) > 1) else '0'+ str(timezone.now().day)
            month = str(timezone.now().month) if (len(str(timezone.now().month)) > 1) else '0'+ str(timezone.now().month)
            year = str(timezone.now().year)[-2:]
            return day + month + year + str(random.randint(100, 999))
        new_transaction_id = generate_transaction_id()
        while True:
            if new_transaction_id in [id.transaction_id for id in Transaction.objects.all()]:
                new_transaction_id = generate_transaction_id()
            else:
                break
        new_transaction = Transaction(transaction_id=new_transaction_id, student_id=student_id, tutor_number=hired_tutor_number,
                                      total_amount_due=total_amount_due, num_of_days_per_week=num_of_days_per_week,
                                      hours_per_day=num_of_hours_per_day, tutor_payment=tutor_total_payment_and_transport_allowance)
        new_transaction.save()

        context = {'tutor': tutor, 'tutor_charge_per_hour': format_currency(tutor.charge), 'tutor_user': tutor_user,
                   'total_tuition': format_currency(total_tuition), 'transport_fare_per_day': format_currency(transport_fare_per_day),
                   'total_transport_fare': format_currency(total_transport_fare), 'total_amount_due': format_currency(total_amount_due),
                   'transaction_number': new_transaction.transaction_id}

        # a point of creating notification for student and tutor

        notification_title = 'Transaction: %s'%(new_transaction_id)
        student_message = 'Transaction %s has been made between you and tutor %s on the %s' %(new_transaction_id, hired_tutor_number, timezone.now())
        notification_for_new_transaction = Notification(related_transaction=new_transaction_id, tutor_number=hired_tutor_number, title=notification_title, message_for_student=student_message)
        notification_for_new_transaction.save()
        return render(request, 'transaction/confirm_transaction.html', context)
    return redirect('/student/select_tutor/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def checkout_payment(request, trans_id):
    try:
        if request.user.student:
            signed_in_student_id = request.user.username
            transaction_number = str(trans_id)
            transaction = None
            student_can_view_transaction = None
            try:  # Assuming trans_id is a valid Transaction I.D.
                transaction = Transaction.objects.get(transaction_id=transaction_number)
                if transaction.student_id is None:
                    transaction.student_id = request.user.username
                    transaction.save()
                    new_notification = Notification.objects.get(related_transaction=transaction_number)
                    new_notification.save()
                    student_can_view_transaction = True
                elif transaction.student_id == signed_in_student_id:
                    student_can_view_transaction = True
                else:
                    student_can_view_transaction = False
            except transaction.DoesNotExist:  # If trans_id is an invalid Transaction I.D., this suite will then be executed
                transaction = None
                exception_name = 'Transaction does not exist!'
            except Exception as exception_name:  # A defensive mechanism to catch any other form of Exception
                return redirect('/student/select_tutor/')
            finally:
                context = {'transaction_number': transaction_number, 'transaction': transaction, 'student_can_view_transaction': student_can_view_transaction}
                return render(request, 'transaction/checkout_payment.html', context)
    except Exception as e:
        logout(request)
        return redirect('/student/dashboard/')
    # TODO: Properly implement the next 3 lines in some view:
    # tutor = User.objects.get(pk=transaction.tutor_number)
    # tutor.availability = (tutor.availability - 1) if (tutor.availability > 0) else 0
    # tutor.save()
