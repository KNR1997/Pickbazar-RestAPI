import logging

from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied, ObjectDoesNotExist
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def drf_default_with_modifications_exception_handler(exc, ctx):
    """
    Custom exception handler for DRF, mapping Django exceptions to DRF-compatible exceptions
    and providing consistent error responses.
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, ObjectDoesNotExist):
        exc = exceptions.NotFound(detail=str(exc))

    # Delegate to DRF's default exception handler
    response = exception_handler(exc, ctx)

    # Handle unexpected errors (e.g., server errors)
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response(
            {
                "error": "A server error occurred. Please contact support if the issue persists.",
                "details": str(exc),
            },
            status=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Ensure a consistent response format
    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }

    return response
