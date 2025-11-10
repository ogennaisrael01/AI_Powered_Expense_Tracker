from rest_framework import serializers
import email_validator
from django.contrib.auth.password_validation import validate_password as _validate
from .auth_models import CustomUser
from rest_framework.authtoken.models import Token

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
        if user:
            token = Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50, write_only=True)



class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50, 
                                   write_only=True,
                                   required=True,
                                   error_messages= {
                                       "blank": "email cannot be blank",
                                       "reauired": "email is required"
                                   })
    class Meta:
        fields = ["email"]

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=50,
        write_only=True,
        required=True,
        error_messages={
            "blank": "password cannot be blank",
            "required": "password is required"
        }
    )
    confirm_password = serializers.CharField(
        max_length=50,
        write_only=True,
        required=True,
        error_messages={
            "blank": "confirm password cannot be blank",
            "required": "Please confirm your password"

        }
    )

    class Meta:
        fields = ["password", "confirm_password"]

    def validate(self, attrs):
        password = attrs["password"]
        if password:
            _validate(password)

        if password != attrs["confirm_password"]:
            raise serializers.ValidationError("Password mismatch")
        
        return attrs



class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "first_name", "last_name", "is_verified", "currency", "income"]

class ProfileUdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields = ["email", "username", "first_name", "last_name", "currency"]