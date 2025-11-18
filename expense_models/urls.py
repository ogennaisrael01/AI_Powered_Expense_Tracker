from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import (
    RegistrationViewset,
    LoginView,
    VerifyAccountView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    ProfileView

)
from .tracker_views import (
    AccountViewSet,
    TransactionViewSet
)
from .payments_views import (
    DepositView,
    VerifyView,
    WithDrawView
)
from .views import health

router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename="account")
router.register(r'transactions', TransactionViewSet, basename="transaction")

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
    path("", include(router.urls))
]

urlpatterns += [
    path("withdraw/", WithDrawView.as_view(), name="with=draw"),
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("verify/payment", VerifyView.as_view(), name="verify-payments")
]
urlpatterns += [
    path("auth/", include("rest_framework.urls"))
]