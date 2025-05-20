from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.serializers import CustomTokenObtainPairSerializer, CustomerTokenObtainPairSerializer, \
    UserRegistrationSerializer
from users.models import User
from users.services.user_services import user_create


# Create your views here.
class UserRegistrationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Prepare response data
        response_data = {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "display_name": user.display_name,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        # name = serializers.CharField(required=True)
        password = serializers.CharField(required=True)

    class OutputSerializer(serializers.Serializer):
        email = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Endpoint Operation Description",
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING, description="Field 1 Description"),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING, description="Field 2 Description"),
            },
            required=['email', 'password']

        )
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(
            **serializer.validated_data
        )

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        data = {
            "email": user.email,
            "token": access_token,
            "refresh": str(refresh),
        }

        return Response(data, status=status.HTTP_201_CREATED)


# Serializer to validate the passwords
class ChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the authenticated user
        user = request.user

        # Validate the old and new password fields
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["oldPassword"]
            new_password = serializer.validated_data["newPassword"]

            # Check if the old password is correct
            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Validate the new password (checks for strength, etc.)
                validate_password(new_password, user)
            except serializers.ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password and save the user
            user.set_password(new_password)
            user.save()

            # Update the session auth hash to keep the user logged in after password change
            update_session_auth_hash(request, user)

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
