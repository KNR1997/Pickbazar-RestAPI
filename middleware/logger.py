import logging
import time
from typing import Union

from django.http import HttpRequest
from rest_framework.request import Request

from common.models import APIActivityLog
from utils.ip_address import get_client_ip

api_logger = logging.getLogger("chandula.api.request")


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _should_log_route(self, request: Union[Request, HttpRequest]) -> bool:
        """
        Determines whether a route should be logged based on the request and status code.
        """
        # Don't log health checks
        if request.path == "/" and request.method == "GET":
            return False
        return True

    def __call__(self, request):
        # get the start time
        start_time = time.time()

        # Get the response
        response = self.get_response(request)

        # calculate the duration
        duration = time.time() - start_time

        # Check if logging is required
        log_true = self._should_log_route(request=request)

        # If logging is not required, return the response
        if not log_true:
            return response

        user_id = (
            request.user.id
            if getattr(request, "user")
               and getattr(request.user, "is_authenticated", False)
            else None
        )

        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Log the request information
        api_logger.info(
            f"{request.method} {request.get_full_path()} {response.status_code}",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": int(duration * 1000),
                "remote_addr": get_client_ip(request),
                "user_agent": user_agent,
                "user_id": user_id,
            },
        )

        # return the response
        return response


class APITokenLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_body = request.body
        response = self.get_response(request)
        self.process_request(request, response, request_body)
        return response

    def process_request(self, request, response, request_body):
        api_key_header = "X-Api-Key"
        api_key = request.headers.get(api_key_header)
        # If the API key is present, log the request
        if api_key:
            try:
                APIActivityLog.objects.create(
                    token_identifier=api_key,
                    path=request.path,
                    method=request.method,
                    query_params=request.META.get("QUERY_STRING", ""),
                    headers=str(request.headers),
                    body=(request_body.decode("utf-8") if request_body else None),
                    response_body=(
                        response.content.decode("utf-8") if response.content else None
                    ),
                    response_code=response.status_code,
                    ip_address=get_client_ip(request=request),
                    user_agent=request.META.get("HTTP_USER_AGENT", None),
                )

            except Exception as e:
                api_logger.exception(e)
                # If the token does not exist, you can decide whether to log this as an invalid attempt

        return None
