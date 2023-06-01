"""
Core views for API.
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request


@api_view(["GET"])
def health_check(request: Request) -> JsonResponse:
    """Returns successful response."""
    return JsonResponse({"healthy": True})
