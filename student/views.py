import re, random
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, send_mass_mail
from django.contrib.auth.models import User
import datetime
from tutor.views import calculate_tutor_charge_per_hour, update_tutor_profile
from transaction.views import format_currency
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
from django.core.files.storage import default_storage
from student.forms import Address


def properly_format_student_id(student_id):
    return str(student_id).upper()


def student_sign_up(request):
    users = User.objects

    if request.method == 'POST':
        def is_used_student_id(new_id):
            try:
                users.get(username=new_id)
                return False
            except Exception:
                return True

        student_id = "A1000"
        while not is_used_student_id(student_id):
            student_id = random.choice(
                ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U',
                 'V', 'W', 'X', 'Y', 'Z']) + str(random.randint(1000, 9999))

        username = student_id
        password = request.POST['password']
        first_name = request.POST['first_name'].capitalize()
        last_name = request.POST['last_name'].capitalize()
        email = request.POST['email'].lower()
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        address = request.POST['address']

        new_user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
        user_id = new_user.id
        new_student = Student(user_id=user_id)
        new_student.user_id = user_id
        new_student.gender = gender
        new_student.phone_number = phone_number
        new_student.home_address = address
        try:
            new_student.photo = request.FILES['profile_photo']
        except Exception:
            new_student.photo = None
        new_student.save()
        # the next few lines before the return statement will email the Student's username to him/her
        student_login_link = 'http://logeeksatutors.com/student/sign_in/'
        email_subject = 'LOGEEKS \'A\'-TUTORS WELCOMES YOU'
        email_message = 'Your Username (Student ID) is ' + str(student_id) + '. \n Follow the link below to login into ' \
                                                                             'your Student Account. \n' \
                                                                             + str(student_login_link) + '\n\n' \
                                                                             'Thanks for choosing Logeeks! \n' \
                                                                             'Best Regards\n' \
                                                                             'Logeeks \'A\'-Tutors (Scientific).'

        # TODO: uncomment the next line to test its functionality, when there's internet connection;
        send_mail(email_subject, email_message, 'info@logeeksatutors.com', [str(email)])
        # new_user.email_user(subject=email_subject, message=email_message, from_email='info@logeeksatutors.com')
        context = {'new_student_first_name': first_name, 'new_student_email': email}
        return render(request, 'student/student_sign_up_complete.html', context)

    context = {}
    return render(request, 'student/student_sign_up.html', context)


# @login_required(login_url='/student/sign_in/', redirect_field_name='next')
def select_tutor(request):
    try:
        if request.user.student:
            valid_select_tutor_link = 'student/signed_in_student_select_tutor_page.html'
    except Exception:
        valid_select_tutor_link = 'student/student_select_tutor.html'
    context = {}
    return render(request, valid_select_tutor_link, context)


# @login_required(login_url='/student/sign_in/', redirect_field_name='next')
def hire_tutor(request):
    try:
        if request.user.student:
            valid_hire_tutor_link = 'student/signed_in_student_hire_tutor.html'
    except Exception:
        valid_hire_tutor_link = 'student/student_hire_tutor.html'

    if request.method == 'POST':
        subject = request.POST['subject']
        client_lga = request.POST['lga']
        page_num_to_be_displayed = int(request.POST['page_no'])

        valid_tutors_list = []
        tutor_model = Tutor
        # tutor_user = None
        all_tutors_list = tutor_model.objects.all()
        for tutor in all_tutors_list:
            if (client_lga == tutor.lga1 or client_lga == tutor.lga2 or client_lga == tutor.lga3) and subject == tutor.subject:
                if tutor.is_visible:
                    valid_tutors_list.append(tutor)
        for tutor in valid_tutors_list:
            # tutor_user = tutor.user
            update_tutor_profile(tutor)
            tutor.charge = format_currency(tutor.charge)

        num_of_matched_query = len(valid_tutors_list)
        # if the number of tutors per page must be changed, reset maximum_num_of_tutors_per_page = the new value.
        # but the valid minimum value for maximum_num_of_tutors_per_page should be = 3
        maximum_num_of_tutors_per_page = 9
        num_of_tutors_per_row = 3
        number_of_row = [i for i in range(0, (maximum_num_of_tutors_per_page+1), num_of_tutors_per_row)]
        limit_dict = {}
        upper_bound = maximum_num_of_tutors_per_page
        lower_bound = 0
        page_num = 1
        length_uncovered = len(valid_tutors_list)
        while length_uncovered//maximum_num_of_tutors_per_page > 0 or (length_uncovered % maximum_num_of_tutors_per_page > 0 and length_uncovered > 0):
            limit_dict[page_num] = valid_tutors_list[lower_bound : upper_bound]
            page_num += 1
            lower_bound = upper_bound
            predicted_upper_bound = upper_bound + maximum_num_of_tutors_per_page
            if num_of_matched_query > predicted_upper_bound:
                upper_bound = predicted_upper_bound
            else:
                upper_bound = num_of_matched_query
            length_uncovered -= maximum_num_of_tutors_per_page

        available_pages = list(limit_dict.keys())
        if available_pages:
            maximum_page_no = max(available_pages)
            minimum_page_no = min(available_pages)
        else:
            maximum_page_no = 0
            minimum_page_no = 0

        if limit_dict:
            page_to_be_displayed = limit_dict.get(page_num_to_be_displayed, None)
        else:
            page_to_be_displayed = []

        context = {'tutors_to_be_displayed': page_to_be_displayed, 'number_of_rows': number_of_row, 'lga': client_lga,
                   'subject': subject, 'query_match': num_of_matched_query, 'pages': available_pages,
                   'current_page': page_num_to_be_displayed, 'last_page': maximum_page_no,
                   'first_page': minimum_page_no, 'col_sm_value': (12 // num_of_tutors_per_row)}

        return render(request, valid_hire_tutor_link, context)
    return redirect('/student/select_tutor/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_dashboard(request):
    try:
        if request.user.student:
            user = request.user
            student = user.student
            student_photo = student.photo.url if (student.photo) else None
            unread_notifications = Notification.objects.filter(read_status=False, student_id=request.user.username)
            context = {'user': user, 'student': student, 'student_photo': student_photo,
                       'number_of_unread_notifications': len(unread_notifications)}
            return render(request, 'student/student_dashboard.html', context)
    except Exception:
        logout(request)
        return redirect('/student/dashboard/')


def student_sign_in(request):
    if request.GET:
        next_url=request.GET['next']
    else:
        next_url = '/student/dashboard/'
    error_message = False
    if next_url != '/student/dashboard/':
        additional_message = 'Please sign in continue'
    else:
        additional_message = None
    context = {'error_message': error_message, 'next_url': next_url, 'additional_message': additional_message}
    return render(request, 'student/student_sign_in.html', context)


def authenticating(request):
    error_message = None
    student_id = None
    if request.POST:
        student_id = request.POST['username']
        password = request.POST['password']
        next_url = request.POST['next']
        student = authenticate(username=properly_format_student_id(student_id), password=password)
        if student:
            if student.is_active:
                login(request, student)
                return redirect(next_url)
            else:
                error_message = 'Sorry, but this Account has been deleted!'
        else:
            error_message = 'Invalid student Info'

    if request.GET:
        next_url = request.GET['next']
    else:
        next_url = '/student/dashboard/'
    context = {'error_message': error_message, 'next_url': next_url, 'student_id': student_id}
    return render(request, 'student/student_sign_in.html', context)


def student_sign_out(request):
    logout_student = False
    if request.method == 'POST':
        sign_out = request.POST['sign_out']
        logout_student = True
        logout(request)
    context = {'user_just_logged_out': logout_student}
    return redirect('/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def update_student_password(request):
    try:
        if request.user.student:
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
                elif (user.first_name.lower() or user.last_name.lower() or user.student.middle_name.lower()) == new_password.lower():
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
                    return HttpResponsePermanentRedirect('/student/password_update_successful')
            context = {'password_update_failed': password_update_failed, 'password_update_error_message': error_message}
            return render(request, 'student/student_password_update.html', context)
    except Exception:
        logout(request)
        return HttpResponseRedirect('/student/student_change_password/')


def password_update_successful(request):
    return render(request, 'student/student_password_update_successful.html')


def student_reset_password(request):
    logout(request)
    template_name = 'student/student_password_reset.html'
    context = {}
    error_occurred = None
    if request.method == 'POST':
        recipient_username = request.POST['recipient_username']
        try:
            user = User.objects.get(username=properly_format_student_id(recipient_username))
            uidb64 = recipient_username
            token_generator = default_token_generator.make_token(user)
            context = {'uidb64': uidb64, 'token': token_generator}
            error_occurred = False
            user_email = user.email
            from_email = 'info@logeeksatutors.com'
            subject = 'Password reset link'
            message = 'Dear ' + str(user.first_name) + ', follow the link below to reset your password:\n' + \
                      'localhost:8000/student/student_password_reset_confirm/' + str(uidb64) + '/' + str(token_generator)

            send_mail(subject, message, from_email, [user_email])

            return redirect('/student/student_password_reset_done/')

        except Exception:
            error_occurred = True
    if error_occurred:
        context = {'error_occurred': error_occurred, 'incorrect_username': recipient_username}
    return render(request, template_name, context)


def student_password_reset_done(request):
    logout(request)
    context = {}
    return render(request, 'student/student_password_reset_done.html', context)


def student_password_reset_confirm(request, uidb64=None, token=None,):
    logout(request)
    recipient_username = uidb64
    user = User.objects.get(username=properly_format_student_id(recipient_username))
    token_generator = default_token_generator
    if user is not None and token_generator.check_token(user, token):
        link_is_valid = True
        message = 'Successful!'
    else:
        link_is_valid = False
        message = 'Failed! This link is invalid'
    context = {'link_is_valid': link_is_valid, 'message': message, 'student_id': recipient_username}
    return render(request, 'student/student_password_reset_confirm.html', context)


def student_set_new_password(request):
    logout(request)
    error_message = None
    password_update_failed = None
    if request.method == 'POST':
        new_password = request.POST['new_password']
        retyped_new_password = request.POST['retyped_new_password']
        recipient_username = request.POST['student_id']
        properly_formatted_recipient_username = properly_format_student_id(recipient_username)
        user = User.objects.get(username=properly_formatted_recipient_username)
        if (new_password != retyped_new_password) and (new_password != ''):
            password_update_failed = True
            error_message = 'The New Password fields does not match!'
        elif (user.first_name.lower() or user.last_name.lower() or user.student.middleName.lower()) == new_password.lower():
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
            return HttpResponsePermanentRedirect('/student/student_password_reset_complete')
    context = {'password_update_failed': password_update_failed, 'error_message': error_message,
               'student_id': recipient_username}
    return render(request, 'student/student_set_new_password.html', context)


def student_password_reset_complete(request):
    logout(request)
    context = {}
    return render(request, 'student/student_password_reset_complete.html', context)


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def account_settings(request):
    try:
        if request.user.student:
            if request.method == 'POST':
                new_phone_number = request.POST['phone_number']
                new_address = request.POST['home_address']
                student = request.user.student
                student.phone_number = new_phone_number
                student.home_address = new_address
                student.save()
            user = request.user
            student = user.student
            unread_notifications = Notification.objects.filter(read_status=False, student_id=request.user.username)
            context = {'user': user, 'student': student, 'location_form': Address,
                       'number_of_unread_notifications': len(unread_notifications)}
            return render(request, 'student/account_settings.html', context)
    except Exception:
        logout(request)
        return HttpResponseRedirect('/student/account_settings/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def transaction_archive(request):
    try:
        if request.user.student:
            this_student_id = request.user.username
            this_student_transactions = Transaction.objects.filter(student_id=this_student_id)
            for trans in this_student_transactions:
                trans.total_amount_due = format_currency(trans.total_amount_due)
            context = {'this_student_transactions': this_student_transactions}
            return render(request, 'student/transaction_archive.html', context)
    except Exception:
        logout(request)
        return redirect('/student/transaction_archive/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def view_transaction(request, trans_id):
    currently_viewed_transaction = Transaction.objects.get(transaction_id=trans_id)
    currently_viewed_transaction.total_amount_due = format_currency(currently_viewed_transaction.total_amount_due)
    if currently_viewed_transaction.student_notified:
        notification = Notification.objects.get(related_transaction=trans_id)
        notification.read_status = True
        notification.save()
    context = {'the_transaction': currently_viewed_transaction}
    return render(request, 'student/view_a_transaction.html', context)


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_diary(request):
    try:
        if request.user.student:
            if request.method == 'POST':
                student = request.user.student
                student.diary = request.POST['student_diary_content']
                student.save()
            user = request.user
            student = user.student
            diary = student.diary
            context = {'diary_content': diary, 'user': user, 'student': student}
            return render(request, 'student/student_diary.html', context)
    except Exception:
        logout(request)
        return redirect('/student/diary/')


def did_you_know_facts(request):
    return render(request, 'student/did_you_know.html')


def signed_in_student_select_tutor(request):
    return render(request, 'student/signed_in_student_select_tutor_modal.html')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_change_color(request):
    try:
        if request.user.student:
            if request.method == 'POST':
                new_choice_color = request.POST['choice_color']
                request.user.student.choice_color = new_choice_color
                request.user.student.save()
            return redirect('/student/account_settings/')
    except Exception:
        logout(request)
        return redirect('/student/dashboard/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_change_photo(request):
    try:
        if request.user.student:
            student = request.user.student
            if request.method == 'POST':
                new_profile_photo = request.FILES['new_profile_photo']
                try:
                    if student.photo.url:
                        default_storage.delete(student.photo.path)
                except Exception:
                    pass
                student.photo = new_profile_photo
                student.save()
            return redirect('/student/account_settings/')
    except Exception:
        logout(request)
        return redirect('/student/dashboard/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_remove_photo(request):
    try:
        if request.user.student:
            student = request.user.student
            if request.method == 'POST':
                default_storage.delete(student.photo.path)
                student.photo = None
                student.save()
            return redirect('/student/account_settings/')
    except Exception:
        logout(request)
        return redirect('/student/dashboard/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def science_world(request):
    try:
        if request.user.student:
            context = {}
            return render(request, 'student/science_world.html', context)
    except Exception:
        logout(request)
        return redirect('/student/science_world/')


@login_required(login_url='/student/sign_in/', redirect_field_name='next')
def student_notification(request):
    try:
        if request.user.student:
            all_notifications = Notification.objects.all()
            this_student_notifications = []
            this_student_id = request.user.username
            this_student_transactions = Transaction.objects.filter(student_id=this_student_id)
            for each_transaction in this_student_transactions:
                for each_notification in all_notifications:
                    if each_transaction.transaction_id == each_notification.related_transaction:
                        each_notification.student_id = this_student_id
                        each_notification.save()
                        each_transaction.student_notified = True
                        each_transaction.save()
            for notification in all_notifications:
                if notification.student_id == this_student_id:
                    this_student_notifications.append(notification)

            context = {'notifications_to_display': this_student_notifications}
            return render(request, 'student/student_notification.html', context)
    except Exception:
        logout(request)
        return redirect('/student/dashboard/')