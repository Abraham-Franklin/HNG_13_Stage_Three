from django.urls import path
from .views import GeoNationAgentView

urlpatterns = [
    path("", GeoNationAgentView.as_view(), name="agent-view")
]