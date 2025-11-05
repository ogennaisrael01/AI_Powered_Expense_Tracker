from django.urls import path
from .auth_views import RegistrationViewset

urlpatterns = [
    path("register/", RegistrationViewset.as_view(), name="register")
]