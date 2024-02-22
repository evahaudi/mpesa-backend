# serializers.py
from rest_framework import serializers
from users.models import Users, Payment,Manager, PaymentTransaction


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
        
class ManagerSignupView(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "username",
            "email",
            "fullname",
            "birthdate",
            "location",
            "experienceyears",
            "phone",
            "department",
            "updated_by",
            "password",
            "password2",
            "role",
            "is_active"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self, **kwargs):
        fullname = self.validated_data["fullname"]
        username = self.validated_data["username"]
        email = self.validated_data["email"]
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]
        location = self.validated_data["location"]
        birthdate = self.validated_data["birthdate"]
        phone = self.validated_data["phone"]
        is_active=self.validated_data["is_active"]
        department = self.validated_data["department"]
        experienceyears = self.validated_data["experienceyears"]
        role = self.validated_data["role"]

        if password != password2:
            raise serializers.ValidationError({"error": "Passwords do not match"})

        user = Users(
            fullname=fullname,
            username=username,
            email=email,
            location=location,
            birthdate=birthdate,
            phone=phone,
            is_active=is_active,
            department=department,
            experienceyears=experienceyears,
            role=role,
        )
        user.set_password(password)
        user.is_manager = True
        user.save()
        Manager.objects.create(user=user)
        return user

class PaymentSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    user = UsersSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "username",
            "fullname",
            "email",
            "password2",
            "cuisine_specialty",
            "experienceyears",
        ]
        extra_kwargs = {"password": {"write_only": True}}


