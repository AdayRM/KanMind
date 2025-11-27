from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .serializers import AccountSerializer, LoginSerializer, RegistrationSerializer

from auth_app.models import Account

""" 
This view is only for the list of accounts
"""


class AccountView(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


""" 
This view handles the registration
"""


class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


""" 
This view handles the login. 
DRF provides a view to get the token for an user but this one only returns the token. 
As we want to provide more data in the response, we need to create a custom view.
https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
"""


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

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
