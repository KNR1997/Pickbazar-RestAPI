from django.http import Http404
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from users.permissions import IsSuperAdminOrStoreOwner
from users.selectors import user_get, user_list, profile_get_by_user, customer_list
from users.serializers import AddressSerializer, ProfileSerializer, GroupSerializer
from users.services.user_services import user_create, user_update


# TODO: When JWT is resolved, add authenticated version


class UserDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        addresses = AddressSerializer(many=True)

    def get(self, request, user_id):
        user = request.user

        if user is None:
            raise Http404

        data = self.OutputSerializer(user).data

        return Response(data)


class CustomerListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        email = serializers.EmailField(required=False)
        groups = GroupSerializer(required=False, many=True)
        is_active = serializers.BooleanField(required=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        customers = customer_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=customers,
            request=request,
        )


class UserCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(
            **serializer.validated_data
        )

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = UserDetailApi.OutputSerializer(user).data

        return Response(data)


class AddressInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)  # Include if updating an existing address
    title = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=["billing", "shipping"])
    is_default = serializers.BooleanField(default=False)
    zip = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    street_address = serializers.CharField(required=True)


# Profile serializer to handle nested profile updates
class ProfileInputSerializer(serializers.Serializer):
    bio = serializers.CharField(required=False, allow_null=True)
    contact = serializers.CharField(required=False, allow_null=True)


class UserUpdateApi(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        # Note: Currently, those are not actual user fields, but rather an example
        name = serializers.CharField(required=False)
        profile = ProfileInputSerializer(required=False)  # Include profile as an object
        address = serializers.ListSerializer(child=AddressInputSerializer(), required=False)

    def put(self, request, user_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_get(user_id)

        if user is None:
            raise Http404

        user = user_update(user=user, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = UserDetailApi.OutputSerializer(user).data

        return Response(data)


class MeApi(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request):
        # Get the currently authenticated user
        requested_user = request.user

        # Fetch profile details
        profile = profile_get_by_user(base_user=requested_user)
        # try:
        #     profile = Profile.objects.get(user=requested_user)
        # except Profile.DoesNotExist:
        #     profile = None

        user_data = {
            "id": str(requested_user.id),
            "name": requested_user.name,
            "email": requested_user.email,
            "addresses": AddressSerializer(requested_user.addresses.all(), many=True).data,
            "profile": ProfileSerializer(profile).data if profile else None
        }

        return Response(user_data)
