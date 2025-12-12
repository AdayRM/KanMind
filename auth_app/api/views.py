"""Authentication and account API views for KanMind.

Provides endpoints for listing accounts, user registration, and login.
Includes a `build_auth_response` helper to standardize auth responses
with token and user metadata.
"""

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .serializers import LoginSerializer, RegistrationSerializer


"""
This view file exposes endpoints related to authentication and accounts.
`AccountView` is limited to listing accounts.
"""


def build_auth_response(*, user, status_code=200):
    """Create a standardized authentication response.

    Args:
        user: Authenticated Django user instance.
        status_code: HTTP status code for the response.

    Returns:
        DRF Response containing auth token and user metadata.
    """
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "fullname": user.account.fullname,
        },
        status=status_code,
    )


class RegistrationView(generics.CreateAPIView):
    """Register a new user and return an auth response.

    Accepts user credentials and profile data via
    `RegistrationSerializer`. On success, returns a tokenized auth
    response similar to login.
    """

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Validate input, create user, and return token + metadata."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = serializer.instance
        return build_auth_response(user=user, status_code=201)


class LoginView(APIView):
    """Authenticate a user and return token plus user metadata.

    Uses `LoginSerializer` to validate credentials. Returns a standardized
    response containing token, user id, email, and fullname.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and respond with tokenized auth payload."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return build_auth_response(user=user)
