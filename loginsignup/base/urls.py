from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import path, include



from .views import (
    student_signup_view,
    welcome,
    teacher_info,
    student_info,
    teacher_signup_view,
    login_view

    
)
from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import path


app_name = 'base'

urlpatterns = [
    path("", welcome, name="welcome"),                     # Welcome page
    path("student_signup/", student_signup_view, name="student_signup"),
    path("signup_teach/", teacher_signup_view, name="teacher_signup"),
    path("teacher_info/", teacher_info, name="teacher_info"),
    path("student_info/", student_info, name="student_info"),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),  # Django auth URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name = 'password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(), name = 'password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(), name = 'password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name = 'password_reset_complete'),
    path("accounts/", include("django.contrib.auth.urls")),
]
