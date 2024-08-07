
from django.urls import path 
from .views import UserRegistrationView ,UserLoginView , UserLogoutview ,UserBankAccountUpdateView
urlpatterns = [
    path('register/', UserRegistrationView.as_view() ,name='register'),
    path('login/',  UserLoginView.as_view(),name='login'),
    path('logout/', UserLogoutview.as_view() ,name='logout'),
    path('profile/', UserBankAccountUpdateView.as_view() ,name='profile'),
]
