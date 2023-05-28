"""
URL mappings for User API
"""
from django.urls import path

from user import views

app_name = "user"  # reverse() will return "user:path_name"

urlpatterns = [
    path("create", views.CreateUserView.as_view(), name="create"),
]
