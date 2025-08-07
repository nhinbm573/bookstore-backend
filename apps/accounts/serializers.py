from rest_framework import serializers
from .models import Account


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Account
        fields = ["email", "password", "phone", "full_name", "birthday"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        account = Account.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            full_name=validated_data["full_name"],
            birthday=validated_data["birthday"],
            password=password,
        )
        return account
