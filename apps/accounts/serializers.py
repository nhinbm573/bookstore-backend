from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Account
import requests
from django.conf import settings


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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    captcha = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        captcha = attrs.get("captcha", "")

        request = self.context.get("request")
        ip_address = request.META.get("REMOTE_ADDR", "unknown")

        cache_key = f"failed_attempts:{email}:{ip_address}"
        failed_attempts = cache.get(cache_key, 0)

        if failed_attempts >= 3:
            if not captcha:
                raise serializers.ValidationError(
                    {
                        "message": "Captcha verification required after multiple failed attempts."
                    }
                )

            if not self.verify_captcha(captcha):
                raise serializers.ValidationError(
                    {"message": "Invalid captcha. Please try again."}
                )

        user = authenticate(request=request, username=email, password=password)

        if not user:
            new_failed_attempts = failed_attempts + 1
            cache.set(cache_key, new_failed_attempts, timeout=1800)  # 30 minutes

            if new_failed_attempts >= 3:
                raise serializers.ValidationError(
                    {
                        "message": "Invalid credentials. Captcha required for next attempt."
                    }
                )
            else:
                raise serializers.ValidationError({"message": "Invalid credentials."})

        if not user.is_active:
            raise serializers.ValidationError({"message": "Invalid credentials."})

        cache.delete(cache_key)

        attrs["user"] = user
        return attrs

    def verify_captcha(self, captcha_token):
        """
        Verify Google reCAPTCHA token with Google's API
        """
        recaptcha_secret = settings.RECAPTCHA_SECRET_KEY

        if not recaptcha_secret:
            return True

        verification_url = "https://www.google.com/recaptcha/api/siteverify"
        data = {
            "secret": recaptcha_secret,
            "response": captcha_token,
        }

        try:
            response = requests.post(verification_url, data=data, timeout=5)
            result = response.json()
            return result.get("success", False)
        except Exception:
            return False


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        try:
            refresh = RefreshToken(refresh_token)
            user = refresh.payload.get("user_id")

            if not user:
                raise serializers.ValidationError({"message": "Invalid token."})

            attrs["refresh"] = refresh
            attrs["access"] = refresh.access_token

        except TokenError:
            raise serializers.ValidationError({"message": "Invalid or expired token."})

        return attrs
