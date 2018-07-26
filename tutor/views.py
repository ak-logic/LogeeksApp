import re
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, send_mass_mail
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from tutor.models import Tutor
from transaction.models import Transaction
from django.contrib.auth.models import Permission
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth import views
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from image_cropping.utils import get_backend


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


def properly_format_tutor_number(tutor_number):
    """
    This function ensures the tutor_number has the proper format of a typical tutor number. E.g 0004PHY
    :param tutor_number: (str). The current Tutor's number
    :return: a proper format of tutor's number like 0002MTH, instead of 02mth.
    """
    answer = ''
    stringed_tutor_number = str(tutor_number)
    numerical_part_of_tutor_number = stringed_tutor_number[:-3]
    subject_id_of_tutor_number = (stringed_tutor_number[-3:]).upper()
    if len(numerical_part_of_tutor_number) >= 4:
        numerical_part_of_tutor_number = numerical_part_of_tutor_number[-4:]
    num_list = []
    for i in numerical_part_of_tutor_number:
        num_list.append(i)

    while len(num_list) != 4:
        num_list.insert(0, '0')

    for char in num_list:
        answer += char
    return answer + subject_id_of_tutor_number


def calculate_tutor_charge_per_hour(tutor_experience, tutor_rating, tutor_recommendation, tutor_qualification):
    """
    This function accepts a Tutor's key info to calculate what amount Tutor should earn per hour.

    :param tutor_experience: (int). Years of experience as a Tutor
    :param tutor_rating: (float). Tutor's cumulative rating/reviews from past all tutor's previous clients
    :param tutor_recommendation: (float). Tutor's level of Trust.
    :param tutor_qualification: (float). Academic Qualification of the Tutor
    :return: Returns a float, which is the Tutor's worth per hour (in Naira) calculated based on the four parameters.
    """
    MAX_AMOUNT = 4000  # Maximum Tutor Charge per Hour
    recommendation_point = 5  # Of the total point, this is the weight the tutor's recommendation carries.
    qualification_point = 5  # Of the total point, this is the weight the tutor's Academic Qualifications carries.
    rating_point = 5  # Of the total point, this is the weight the tutor's past [cumulative] Rating carries.
    experience_point = 5  # Of the total point, this is the weight the tutor's years of experience carries.
    total_point = 20  # And here is the sum total of the entire points.

    # tutor_experience = 1 if (tutor_experience <= 1) else tutor_experience

    years_of_experience = experience_point if (tutor_experience >= experience_point) else tutor_experience
    num_of_star_rating = rating_point if (tutor_rating>=rating_point) else tutor_rating
    recommendation = tutor_recommendation if (tutor_recommendation < recommendation_point) else recommendation_point
    qualification = tutor_qualification if (tutor_qualification < qualification_point) else qualification_point

    if tutor_rating <= 0:
        total_point -= tutor_rating
        payment_ratio = float(years_of_experience + recommendation + qualification) / total_point
    else:
        payment_ratio = float(years_of_experience + num_of_star_rating + recommendation + qualification) / total_point
    return round((payment_ratio * MAX_AMOUNT), 2)


def update_tutor_profile(a_tutor):
    if (int(timezone.now().year) > int(a_tutor.user.date_joined.year)) and (
                int(timezone.now().month) >= int(a_tutor.user.date_joined.month)):
        years_of_experience = int(timezone.now().year) - int(a_tutor.user.date_joined.year)
        a_tutor.experience = years_of_experience
    valid_rating_value = 0 if (a_tutor.rating <= 0) else a_tutor.rating
    valid_recommendation_value = 0 if (a_tutor.recommendation <= 0) else a_tutor.recommendation
    valid_qualification_value = 1 if (a_tutor.qualification <= 0) else a_tutor.qualification
    a_tutor.rating = valid_rating_value
    a_tutor.recommendation = valid_recommendation_value
    a_tutor.qualification = valid_qualification_value
    a_tutor.charge = calculate_tutor_charge_per_hour(a_tutor.experience, valid_rating_value, valid_recommendation_value,
                                                   valid_qualification_value)
    a_tutor.save()


@login_required(login_url='/tutor/sign_in/', redirect_field_name='next')
def tutor_dashboard(request):
    # try:
    if request.user.tutor:
        if request.method == 'POST':
            # tutor_verification = request.POST['accept_offer']
            transaction_id = request.POST['transaction_id']
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.validated = True
            transaction.tutor_notified = True
            transaction.save()
        user = request.user
        tutor = user.tutor

        update_tutor_profile(tutor)

        # current_year_of_tutor = datetime.timedelta(user.date_joined, weeks=52)

        try:
            tutor_num = user.username
            all_transactions = Transaction.objects.filter(tutor_number=tutor_num)
            for trans in all_transactions:
                if ((trans.date_initialized + datetime.timedelta(days=5)) == timezone.now()) and (not trans.validated):
                    this_object = Transaction(pk=transaction_id)
                    this_object.delete()
            all_transactions = Transaction.objects.filter(tutor_number=tutor_num)
            if len(all_transactions) > 5:
                for trans in all_transactions[5:]:
                    trans.delete()
            all_concerned_transactions = Transaction.objects.filter(tutor_number=tutor_num)
            unvalidated_transactions = []
            for trans in all_concerned_transactions:
                if not trans.tutor_notified:
                    unvalidated_transactions.append(trans)
            is_notification_available = True if (len(unvalidated_transactions) != 0) else False
            num_of_notifications = len(unvalidated_transactions)
        except Transaction.DoesNotExist:
            is_notification_available = False
            num_of_notifications = 0
        context = {'user': user, 'tutor': tutor, 'notifications': unvalidated_transactions,
                   'is_notification_available': is_notification_available, 'num_of_notifications': num_of_notifications}
        tutor.charge = format_currency(tutor.charge)
        return render(request, 'tutor/tutor_dashboard.html', context)
    # except Exception:
    #     logout(request)
    #     return redirect('/tutor/dashboard/')


def tutor_sign_in(request):
    if request.GET:
        next_url=request.GET['next']
    else:
        next_url = '/tutor/dashboard/'
    error_message = False
    context = {'error_message': error_message, 'next_url': next_url}
    return render(request, 'tutor/tutor_sign_in.html', context)


def authenticating(request):
    error_message = None
    submited_username = None
    if request.POST:
        tutor_number = request.POST['username']
        password = request.POST['password']
        next_url = request.POST['next']
        TUTOR = authenticate(username=properly_format_tutor_number(tutor_number), password=password)
        if TUTOR is not None:
            if TUTOR.is_active:
                login(request, TUTOR)

                # The Tutor's charge/hour is calculated here, just before the dashboard loads
                user = request.user
                tutor = user.tutor

                update_tutor_profile(tutor)

                # At this point, the Tutor's charge has been updated and saved to database
                # before redirecting to the next url

                return HttpResponsePermanentRedirect(next_url)
            else:
                error_message = 'Sorry, but this Account has been deleted!'
        else:
            error_message = 'Invalid Tutor Info'
            submited_username = tutor_number

    if request.GET:
        next_url = request.GET['next']
    else:
        next_url = '/tutor/dashboard/'
    context = {'error_message': error_message, 'next_url': next_url, 'submited_username': submited_username}
    return render(request, 'tutor/tutor_sign_in.html', context)


def tutor_sign_out(request):
    logout_tutor = False
    if request.method == 'POST':
        sign_out = request.POST['sign_out']
        logout_tutor = True
        logout(request)
    context = {'user_just_logged_out': logout_tutor}
    return redirect('/')


@login_required(login_url='/tutor/sign_in/', redirect_field_name='next')
def update_tutor_password(request):
    try:
        if request.user.tutor:
            password_update_failed = False
            error_message = None
            if request.method == 'POST':
                old_password = request.POST['current_password']
                new_password = request.POST['new_password']
                retyped_new_password = request.POST['retyped_new_password']
                user = request.user
                if new_password != retyped_new_password:
                    password_update_failed = True
                    error_message = 'The New Password fields does not match!'
                elif not user.check_password(old_password):
                    password_update_failed = True
                    error_message = 'Current Password typed is incorrect'
                elif (user.first_name.lower() or user.last_name.lower() or user.tutor.middle_name.lower()) == new_password.lower():
                    password_update_failed = True
                    error_message = 'Your new password should not be too similar to your other Personal information!'
                elif re.match(r'[0-9]+', new_password):
                    password_update_failed = True
                    error_message = 'Your password cannot be entirely numeric!'
                elif user.email == new_password:
                    password_update_failed = True
                    error_message = 'Your new password is too similar to your email address!'
                else:
                    user.set_password(new_password)
                    user.save()
                    logout(request)
                    return HttpResponsePermanentRedirect('/tutor/password_update_successful')
            context = {'password_update_failed': password_update_failed, 'password_update_error_message': error_message}
            return render(request, 'tutor/tutor_password_update.html', context)
    except Exception:
        logout(request)
        return redirect('/tutor/tutor_change_password/')


def password_update_successful(request):
    return render(request, 'tutor/tutor_password_update_successful.html')


def tutor_reset_password(request):
    logout(request)
    template_name = 'tutor/tutor_password_reset.html'
    context = {}
    error_occurred = None
    if request.method == 'POST':
        recipient_username = request.POST['recipient_username']
        try:
            user = User.objects.get(username=properly_format_tutor_number(recipient_username))
            uidb64 = recipient_username
            token_generator = default_token_generator.make_token(user)
            context = {'uidb64': uidb64, 'token': token_generator}
            error_occurred = False
            user_email = user.email
            from_email = 'info@logeeksatutors.com'
            subject = 'Password reset link'
            message = 'Tutor ' + str(user.first_name) + ', follow the link below to reset your password:\n' + \
                      'localhost:8000/tutor/tutor_password_reset_confirm/' + str(uidb64) + '/' + str(token_generator)

            send_mail(subject, message, from_email, [user_email])

            return redirect('/tutor/tutor_password_reset_done')

        except User.DoesNotExist:
            error_occurred = True
    if error_occurred:
        context = {'error_occurred': error_occurred, 'incorrect_username': recipient_username}
    return render(request, template_name, context)


def tutor_password_reset_done(request):
    logout(request)
    context = {}
    return render(request, 'tutor/tutor_password_reset_done.html', context)


def tutor_password_reset_confirm(request, uidb64=None, token=None,):
    logout(request)
    recipient_username = uidb64
    user = User.objects.get(username=properly_format_tutor_number(recipient_username))
    token_generator = default_token_generator
    if user is not None and token_generator.check_token(user, token):
        link_is_valid = True
        message = 'Successful!'
    else:
        link_is_valid = False
        message = 'Failed! This link is invalid'
    context = {'link_is_valid': link_is_valid, 'message': message, 'tutor_number': recipient_username}
    return render(request, 'tutor/tutor_password_reset_confirm.html', context)


def tutor_set_new_password(request):
    logout(request)
    error_message = None
    password_update_failed = None
    if request.method == 'POST':
        new_password = request.POST['new_password']
        retyped_new_password = request.POST['retyped_new_password']
        recipient_username = request.POST['tutor_number']
        properly_formatted_recipient_username = properly_format_tutor_number(recipient_username)
        user = User.objects.get(username=properly_formatted_recipient_username)
        if (new_password != retyped_new_password) and (new_password != ''):
            password_update_failed = True
            error_message = 'The New Password fields does not match!'
        elif (user.first_name.lower() or user.last_name.lower() or user.tutor.middle_name.lower()) == new_password.lower():
            password_update_failed = True
            error_message = 'Your new password should not be too similar to your other Personal information!'
        elif re.match(r'[0-9]+', new_password):
            password_update_failed = True
            error_message = 'Your password cannot be entirely numeric!'
        elif user.email == new_password:
            password_update_failed = True
            error_message = 'Your new password is too similar to your email address!'
        elif new_password == retyped_new_password:
            user.set_password(new_password)
            user.save()
            return HttpResponsePermanentRedirect('/tutor/tutor_password_reset_complete')
    context = {'password_update_failed': password_update_failed, 'error_message': error_message,
               'tutor_number': recipient_username}
    return render(request, 'tutor/tutor_set_new_password.html', context)


def tutor_password_reset_complete(request):
    logout(request)
    context = {}
    return render(request, 'tutor/tutor_password_reset_complete.html', context)


@login_required(login_url='/tutor/sign_in/', redirect_field_name='next')
def tutor_profile(request):
    try:
        if request.user.tutor:
            user = request.user
            tutor = user.tutor
            tutor_photo = user.tutor.photo
            tutor_availability = user.tutor.availability
            tutor_address = user.tutor.address
            tutor_phone_number = user.tutor.phone_number
            tutor_lga1 = user.tutor.lga1
            tutor_lga2 = user.tutor.lga2
            tutor_lga3 = user.tutor.lga3

            update_tutor_profile(tutor)

            if request.method == 'POST':
                new_lga1 = request.POST['lga1']
                new_lga2 = request.POST['lga2']
                new_lga3 = request.POST['lga3']
                new_phone_number = request.POST['phone_number']
                new_address = request.POST['address']
                # new_photo = request.POST['photo']
                availability = request.POST['availability']
                tutor_visibility = request.POST['visibility']

                tutor.is_visible = bool(tutor_visibility)
                tutor.availability = availability
                tutor.address = new_address
                tutor.phone_number = new_phone_number
                tutor.lga1 = new_lga1
                tutor.lga2 = new_lga2
                tutor.lga3 = new_lga3
                # if tutor_photo is not None:
                #     user.tutor.photo.delete()
                #     tutor.photo = new_photo
                user.tutor.save()
                return redirect('/tutor/dashboard/')
            tutor.charge = format_currency(tutor.charge)
            context = {'user': user, 'tutor': tutor, 'photo': tutor_photo, 'availability': tutor_availability,
                       'address': tutor_address, 'phone_number': tutor_phone_number, 'lga1': tutor_lga1, 'lga2': tutor_lga2,
                       'lga3': tutor_lga3}
            return render(request, 'tutor/tutor_profile.html', context)
    except Exception:
        logout(request)
        return redirect('/tutor/profile/')


@login_required(login_url='/tutor/sign_in/', redirect_field_name='next')
def transaction_archive(request):
    try:
        if request.user.tutor:
            context = {}
            return render(request, 'tutor/transaction_archive.html', context)
    except Exception:
        logout(request)
        return redirect('/tutor/transaction_archive/')

