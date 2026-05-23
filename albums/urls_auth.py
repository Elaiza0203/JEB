from django.urls import path
from .views_auth import RegisterView

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
]
