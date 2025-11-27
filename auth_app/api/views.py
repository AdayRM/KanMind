from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .serializers import AccountSerializer, LoginSerializer, RegistrationSerializer

from auth_app.models import Account


class AccountView(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer


class LoginView(ObtainAuthToken):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        account = Account.objects.get(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "fullname": account.fullname,
                "email": user.email,
                "user_id": user.pk,
            }
        )
