from django.urls import path
from . import views



lineapp='lineapp'

urlpatterns = [
    path('',views.line_login, name='line_login'),
]


