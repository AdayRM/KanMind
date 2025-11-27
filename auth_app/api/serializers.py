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


# TODO: create also token and send it in the response
class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=100)
    repeated_password = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "fullname", "repeated_password", "user_id"]
        # Declaring fullname as write only in the kwargs does not work because: (docs) Please keep in mind that, if the field has already been explicitly declared on the serializer class, then the extra_kwargs option will be ignored.(docs)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("password does not match")
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        fullname = validated_data.pop("fullname")
        username = fullname.replace(" ", "").strip()
        user = User(email=validated_data["email"], username=username)
        user.set_password(validated_data["password"])
        user.save()
        account = Account(fullname=fullname, user=user)
        account.save()
        return {
            "fullname": fullname,
            "email": validated_data["email"],
            "user_id": user.id,
        }


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
