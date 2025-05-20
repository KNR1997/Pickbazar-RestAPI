from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    is_super_admin = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2',
            'mobile_number', 'display_name', 'first_name', 'last_name', 'is_super_admin'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists."})

        return attrs

    def create(self, validated_data):
        # Remove is_super_admin from validated_data before creating user
        is_super_admin = validated_data.pop('is_super_admin', False)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            mobile_number=validated_data.get('mobile_number', ''),
            display_name=validated_data.get('display_name', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=True
        )

        user.set_password(validated_data['password'])
        user.save()

        # Add to SUPER_ADMIN group if flag is True
        if is_super_admin:
            super_admin_group, created = Group.objects.get_or_create(name='SUPER_ADMIN')
            user.groups.add(super_admin_group)
            # Typically SUPER_ADMIN would also be staff and have superuser privileges
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user  # Get the authenticated user

        # Get user groups
        groups = list(user.groups.values_list("name", flat=True))
        # data["groups"] = groups

        # Set the role as the first group, or None if no groups exist
        data["role"] = groups[0] if groups else None

        # Get user permissions
        data["permissions"] = groups

        # Get user groups
        # data["groups"] = list(user.groups.values_list("name", flat=True))

        # Get user permissions
        # data["permissions"] = list(user.user_permissions.values_list("codename", flat=True))
        # data["permissions"] = list(user.groups.values_list("name", flat=True))

        return data


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Rename 'access' to 'token'
        data["token"] = data.pop("access")

        return data
