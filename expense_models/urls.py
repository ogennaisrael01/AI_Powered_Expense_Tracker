from django.urls import path
from .auth_views import (
    RegistrationViewset,
    LoginView,
    VerifyAccountView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    ProfileView
)
from .tracker_views import (
    AccountView,
    AccountRetreiveView,
)
from .payments_views import (
    DepositView,
    VerifyView
)
from .views import health

urlpatterns = [
    path("health/", health, name="health"),
    path("register/", RegistrationViewset.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify", VerifyAccountView.as_view(), name="verify"),
    path("reset/password/", RequestPasswordResetView.as_view(), name="reset-password"),
    path("password/reset-confirm", PasswordResetConfirmView.as_view(), name="reset-confirm"),
    path("profile/", ProfileView.as_view(), name="profile")

]

urlpatterns += [
    path("accounts/", AccountView.as_view(), name="accounts"),
    path("accounts/<id>/", AccountRetreiveView.as_view(), name="account=detail")
]

urlpatterns += [
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("verify/payment", VerifyView.as_view(), name="verify-payments")
]