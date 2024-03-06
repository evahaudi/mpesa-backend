from django.urls import path
from .views import  CallbackAPIView

urlpatterns = [

    path('mpesa-callback/', CallbackAPIView.as_view(), name='mpesa_callback'),
]
