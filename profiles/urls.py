from django.urls import path
from .views.users import signup

urlpatterns = [
    path('signup', signup, name='signup'),
]