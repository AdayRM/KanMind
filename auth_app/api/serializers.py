"""Authentication and account serializers for KanMind.

Defines serializers to expose account data, register new users, and
authenticate via email/password. Registration handles creating the
`User` and associated `Account`, while login validates credentials and
returns the authenticated user in `validated_data`.
"""

from rest_framework import serializers

from auth_app.models import Account

from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    """Register a new user and create an associated `Account`.

    Accepts `email`, `password`, plus write-only `fullname` and
    `repeated_password` for confirmation. Returns the created `User`.
    """

    fullname = serializers.CharField(write_only=True, max_length=100)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "fullname",
            "repeated_password",
        ]
        # Declaring fullname as write only in the kwargs does not work because: (docs) Please keep in mind that, if the field has already been explicitly declared on the serializer class, then the extra_kwargs option will be ignored.(docs)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        """Ensure `password` matches `repeated_password`."""
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("password does not match")
        return data

    def validate_email(self, value):
        """Ensure email is unique among `User` records."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        """Create `User` and related `Account`; return the `User` instance."""
        fullname = validated_data.pop("fullname")
        username = validated_data["email"]
        user = User(email=validated_data["email"], username=username)
        user.set_password(validated_data["password"])
        user.save()
        account = Account(fullname=fullname, user=user)
        account.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Validate login credentials using email and password.

    On success, injects the authenticated `User` into `validated_data`
    under the `user` key.
    """

    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate via email lookup and `authenticate()` by username."""
        email = data["email"]
        password = data["password"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        data["user"] = user
        return data
