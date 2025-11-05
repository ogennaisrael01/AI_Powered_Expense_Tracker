from rest_framework import serializers
import email_validator
from django.contrib.auth.password_validation import validate_password as _validate
from .auth_models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]

    def validate_password(self, value):
        if value:
            _validate(value)

            return value
        raise serializers.ValidationError(detail="Please enter your password", code=400)
    
    def validate_email(self, value: str):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=True)
        except email_validator.EmailNotValidError as e:
            raise serializers.ValidationError(detail=f"error {e}", code=400)
        if CustomUser.objects.filter(email=valid_email).exists():
            raise serializers.ValidationError("User with this credentials already exists", code=404)
        return valid_email.normalized
    
    def create(self, validated_data):
        # password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        return user