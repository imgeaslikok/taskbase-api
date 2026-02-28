from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """
    Authentication – Login (JWT)
    """

    @classmethod
    def get_token(cls, user):
        """
        Customize JWT claims.

        Keep claims minimal and non-sensitive.
        Good candidates: user id, email, role flags (if stable).
        Avoid: permissions lists, secrets, private data.
        """
        token = super().get_token(user)
        token["email"] = user.email  # optional but convenient for debugging
        return token
