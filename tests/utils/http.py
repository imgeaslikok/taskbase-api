from rest_framework import status

HTTP_400_OR_401 = (
    status.HTTP_400_BAD_REQUEST,
    status.HTTP_401_UNAUTHORIZED,
)

HTTP_401_OR_403 = (
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
)
