from django.conf.urls import url, include
from student import urls
from tutor import urls
from transaction import urls
from homepage import views


app_name = 'homepage'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^student/', include('student.urls')),
    # url(r'^tutor/', include('tutor.urls')),
    url(r'^transaction/', include('transaction.urls')),
    url(r'client/search/', views.query_result, name='query_result')
]
