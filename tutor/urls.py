from django.conf.urls import url, include
import django.contrib.auth.urls
# from django.contrib.auth import views as auth_views

from tutor import views

app_name = 'tutor'
urlpatterns = [
    url(r'^dashboard/$', views.tutor_dashboard, name='tutor_dashboard'),
    url(r'^sign_in/$', views.tutor_sign_in, name='tutor_sign_in'),
    url(r'^authenticating/$', views.authenticating, name='authenticating'),
    url(r'^sign_out/$', views.tutor_sign_out, name='tutor_sign_out'),
    url(r'^tutor_change_password/$', views.update_tutor_password, name='tutor_password_change'),
    url(r'^password_update_successful/$', views.password_update_successful, name='password_update_successful'),
    url(r'^tutor_password_reset/$', views.tutor_reset_password, name='tutor_password_reset'),
    # url(r'^resetting_tutor_password/$', views.resetting_tutor_password, name='resetting_tutor_password'),
    url(r'^tutor_password_reset_done/$', views.tutor_password_reset_done, name='tutor_password_reset_done'),
    url(r'^tutor_password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.tutor_password_reset_confirm, name='tutor_password_reset_confirm'),
    url(r'^tutor_password_reset_complete/$', views.tutor_password_reset_complete, name='tutor_password_reset_complete'),
    url(r'^tutor_set_new_password/$', views.tutor_set_new_password, name='tutor_set_new_password'),
    url(r'^profile/$', views.tutor_profile, name='tutor_profile'),
    url(r'^transaction_archive/$', views.transaction_archive, name='transaction_archive'),
]
