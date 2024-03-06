# serializers.py
from rest_framework import serializers
from users.models import Users, PaymentTransaction


class MPesaResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "transaction_id",
            "amount",
            "status",
            "created_at",
            "updated_at"
           
        ]
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "username",
            "email",
            "fullname",
            "is_chef",
            "is_manager",
            "is_waiter",
            "birthdate",
            "location",
            "experienceyears",
            "phone",
            "created_at",
            "updated_at",
            "department",
            "role",
        ]
        


