from django.urls import path

from .views import USSDCallbackView

urlpatterns = [
    path("", USSDCallbackView.as_view(), name="ussd-callback"),
    path("callback/", USSDCallbackView.as_view(), name="ussd-callback-explicit"),
]
