from rest_framework import serializers

from auth_app.models import Account
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class AccountSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ["id", "fullname", "user", "email"]

    def get_email(self, obj):
        return obj.user.email


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=100, write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    account_fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "account_fullname",
            "fullname",
            "repeated_password",
        ]
        # Declaring fullname as write only in the kwargs does not work because: (docs) Please keep in mind that, if the field has already been explicitly declared on the serializer class, then the extra_kwargs option will be ignored.(docs)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("password does not match")
        return data

    def get_account_fullname(self, obj):
        return obj.account.fullname

    def create(self, validated_data):
        fullname = validated_data.pop("fullname")
        username = fullname.replace(" ", "").strip()
        user = User(email=validated_data["email"], username=username)
        user.set_password(validated_data["password"])
        user.save()
        account = Account(fullname=fullname, user=user)
        account.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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
