from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import LoginSerializer


class LoginView(TokenObtainPairView):
    """
    Issue JWT access and refresh tokens.

    Extends SimpleJWT to allow custom serializer and apply login throttling.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"
    serializer_class = LoginSerializer


class RefreshView(TokenRefreshView):
    """
    Exchange refresh token for new access token.

    Refresh rotation and blacklist behavior are configured in SIMPLE_JWT settings.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"


class LogoutView(APIView):
    """
    Revoke refresh token by adding it to the blacklist.

    Access tokens remain valid until expiration.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            raise ValidationError({"refresh": ["This field is required."]})

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            raise ValidationError({"refresh": ["Invalid token."]})

        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    """
    Return the current authenticated user.

    Used for client bootstrapping and auth verification.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "email": getattr(user, "email", None),
            }
        )
