from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None and isinstance(exc, DatabaseError):
        return Response(
            {"status": "error", "detail": "Database unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return response
