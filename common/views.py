# Python imports
import logging
import traceback
import zoneinfo

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
# Django imports
from django.urls import resolve
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
# Third part imports
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import AuditLog, ErrorLog
from utils.exception_logger import log_exception
from utils.ip_address import get_client_ip
from utils.paginator import BasePaginator

logger = logging.getLogger(__name__)


# Module imports
# from plane.authentication.session import BaseSessionAuthentication


class TimezoneMixin:
    """
    This enables timezone conversion according
    to the user set timezone
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.is_authenticated:
            timezone.activate(zoneinfo.ZoneInfo(request.user.user_timezone))
        else:
            timezone.deactivate()


class BaseViewSet(ModelViewSet, BasePaginator):
    model = None

    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter)

    authentication_classes = [JWTAuthentication]

    filterset_fields = []

    search_fields = []

    def get_queryset(self):
        try:
            return self.model.objects.all()
        except Exception as e:
            log_exception(e)
            raise APIException("Please check the view", status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        try:
            response = super().handle_exception(exc)
            return response
        except Exception as e:
            (
                print(e, traceback.format_exc())
                if settings.DEBUG
                else print("Server Error")
            )
            if isinstance(e, IntegrityError):
                return Response(
                    {"error": "The payload is not valid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if isinstance(e, ValidationError):
                return Response(
                    {"error": "Please provide valid detail"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if isinstance(e, ObjectDoesNotExist):
                return Response(
                    {"error": "The required object does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if isinstance(e, KeyError):
                log_exception(e)
                return Response(
                    {"error": "The required key does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            log_exception(e)
            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)

            if settings.DEBUG:
                from django.db import connection

                print(
                    f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
                )

            return response
        except Exception as exc:
            response = self.handle_exception(exc)
            return exc

    def log_audit(self, action, user, instance, changes):
        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=str(instance.pk),
            changes=changes,
        )

    @property
    def workspace_slug(self):
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        project_id = self.kwargs.get("project_id", None)
        if project_id:
            return project_id

        if resolve(self.request.path_info).url_name == "project":
            return self.kwargs.get("pk", None)

    @property
    def fields(self):
        fields = [
            field for field in self.request.GET.get("fields", "").split(",") if field
        ]
        return fields if fields else None

    @property
    def expand(self):
        expand = [
            expand for expand in self.request.GET.get("expand", "").split(",") if expand
        ]
        return expand if expand else None


class BaseAPIView(APIView):

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        try:
            response = super().handle_exception(exc)
            return response
        except Exception as e:
            request = self.request
            body = None
            if request.content_type == "application/json" and settings.DEBUG:
                body = request._cached_body.decode("utf-8", errors="ignore")

            if isinstance(e, IntegrityError):
                return Response(
                    {"error": "The payload is not valid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if isinstance(e, ValidationError):
                return Response(
                    {"error": "Please provide valid detail"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if isinstance(e, ObjectDoesNotExist):
                return Response(
                    {"error": "The required object does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if isinstance(e, KeyError):
                return Response(
                    {"error": "The required key does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            log_exception(e)
            # ✅ LOG TO YOUR MODEL HERE
            try:
                ErrorLog.objects.create(
                    path=request.path,
                    method=request.method,
                    status_code=500,
                    exception_type=type(exc).__name__,
                    message=str(exc),
                    stack_trace="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                    user=request.user if request and hasattr(request,
                                                             "user") and request.user.is_authenticated else None,
                    headers=str(dict(request.headers)) if request else None,
                    body=body,
                    ip_address=get_client_ip(request) if request else None,
                )
            except Exception as log_exc:
                logger.exception("Failed to write to ErrorLog", exc_info=log_exc)

            return Response(
                {"error": "Something went wrong please try again later"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def dispatch(self, request, *args, **kwargs):
        # Cache the body early
        if not hasattr(request, '_cached_body'):
            try:
                request._cached_body = request.body
            except Exception:
                request._cached_body = b""

        try:
            response = super().dispatch(request, *args, **kwargs)

            if settings.DEBUG:
                from django.db import connection

                print(
                    f"{request.method} - {request.get_full_path()} of Queries: {len(connection.queries)}"
                )
            return response

        except Exception as exc:
            response = self.handle_exception(exc)
            return exc
