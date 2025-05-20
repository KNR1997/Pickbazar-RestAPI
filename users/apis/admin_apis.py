from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from users.permissions import IsSuperAdminOrStoreOwner
from users.selectors import user_get, user_list, admin_list
from users.serializers import GroupSerializer
from users.services.user_services import user_create, user_update


# TODO: When JWT is resolved, add authenticated version


class UserDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()

    def get(self, request):
        user = request.user

        if user is None:
            raise Http404

        data = self.OutputSerializer(user).data

        return Response(data)


class AdminListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)

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

        admins = admin_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=admins,
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


class UserUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        # Note: Currently, those are not actual user fields, but rather an example
        first_name = serializers.CharField(required=True)
        last_name = serializers.CharField(required=True)

    def post(self, request, user_id):
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
