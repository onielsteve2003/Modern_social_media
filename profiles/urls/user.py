from django.urls import path
from ..views.users import signup, login, list_users

urlpatterns = [
    path('signup', signup, name='signup'),
    path('login', login, name='login'),
    path('users', list_users, name='user-list'),
]
