from django.conf.urls import url, include

from student import views

app_name = 'student'
urlpatterns = [
    url(r'^dashboard/$', views.student_dashboard, name='student_dashboard'),
    url(r'^sign_in/$', views.student_sign_in, name='student_sign_in'),
    url(r'sign_up/$', views.student_sign_up, name='student_sign_up'),
    url(r'^authenticating/$', views.authenticating, name='authenticating'),
    url(r'^sign_out/$', views.student_sign_out, name='student_sign_out'),
    url(r'^student_change_password/$', views.update_student_password, name='student_password_change'),
    url(r'^password_update_successful/$', views.password_update_successful, name='password_update_successful'),
    url(r'^student_password_reset/$', views.student_reset_password, name='student_password_reset'),
    # url(r'^resetting_student_password/$', views.resetting_student_password, name='resetting_student_password'),
    url(r'^student_password_reset_done/$', views.student_password_reset_done, name='student_password_reset_done'),
    url(r'^student_password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.student_password_reset_confirm, name='student_password_reset_confirm'),
    url(r'^student_password_reset_complete/$', views.student_password_reset_complete, name='student_password_reset_complete'),
    url(r'^student_set_new_password/$', views.student_set_new_password, name='student_set_new_password'),
    url(r'^account_settings/$', views.account_settings, name='account_settings'),
    url(r'^transaction_archive/$', views.transaction_archive, name='transaction_archive'),
    url(r'^select_tutor/$', views.select_tutor, name='student_select_tutor'),
    url(r'^hire_tutor/$', views.hire_tutor, name='student_hire_tutor'),
    # url(r'^transaction/', include('transaction.urls')),
    url(r'^did_you_know_facts/$', views.did_you_know_facts, name='did_you_know_facts'),
    url(r'^student_change_color/$', views.student_change_color, name='student_change_color'),
    url(r'^transaction/(?P<trans_id>[0-9]+)/$', views.view_transaction, name='view_individual_transaction'),
    url(r'^diary/$', views.student_diary, name='student_diary'),
    url(r'^signed_in_student_select_tutor/$', views.signed_in_student_select_tutor, name='signed_in_student_select_tutor'),
    url(r'^science_world/$', views.science_world, name='student_science_world'),
    url(r'^notification/$', views.student_notification, name='student_notificaiton'),
    url(r'^student_change_photo/$', views.student_change_photo, name='student_change_photo'),
    url(r'^student_remove_photo/$', views.student_remove_photo, name='student_remove_photo')
]
