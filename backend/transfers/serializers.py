from rest_framework import serializers

from .models import Withdrawal


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ("id", "amount", "method", "account_details", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")
