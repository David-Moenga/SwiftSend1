from django.urls import path

from .views import WithdrawalDetailView, WithdrawalListCreateView


urlpatterns = [
    path("withdrawals/", WithdrawalListCreateView.as_view(), name="withdrawal-list-create"),
    path("withdrawals/<int:pk>/", WithdrawalDetailView.as_view(), name="withdrawal-detail"),
]
