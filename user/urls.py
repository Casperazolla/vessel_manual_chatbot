from django.urls import path
from . import views

urlpatterns = [
    # public
    path('signup/',          views.signup_request),
    path('signup/verify/',   views.signup_verify),
    path('login/',           views.login),
    path('forgot-password/', views.forgot_password),
    path('reset-password/',  views.reset_password),
    path('test/',            views.test),

    # protected
    path('profile/',         views.get_profile),
]
