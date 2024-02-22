from django.urls import path
from .views import MpesaPaymentAPIView, ManagerSignupView, CustomAuthToken, CallbackAPIView

urlpatterns = [
    path('mpesa/initiate-payment/', MpesaPaymentAPIView.as_view(), name='mpesa-initiate-payment'),
    path('mpesa-callback/', CallbackAPIView.as_view(), name='mpesa_callback'),
    path("signup/manager/", ManagerSignupView.as_view()),
    path("login/", CustomAuthToken.as_view(), name="auth-token"),
]
