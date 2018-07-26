import re, random
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, send_mass_mail
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from tutor.views import calculate_tutor_charge_per_hour, update_tutor_profile
from tutor.models import Tutor
from student.models import Student
from transaction.models import Transaction
from django.contrib.auth.models import Permission
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth import views
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator


def index(request):
    context = {}

    # Updating all tutors' profile
    # for tutor in Tutor.objects.all():
    #     update_tutor_profile(tutor)

    return render(request, 'homepage/index.html', context)


def query_result(request):
    query_list = str(request.GET['client_query']).split()

    # TODO: Some Regex logic to find query match will be coded here

    context = {}
    return render(request, 'homepage/query_result.html', context)