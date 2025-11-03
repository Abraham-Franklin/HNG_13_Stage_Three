# from django.urls import path
# from .views import GeoNationAgentView

# urlpatterns = [
#     path("", GeoNationAgentView.as_view(), name="agent-view")
# ]


from django.urls import path
from .views import GeoNationAgentView, GeoNationManifestView

urlpatterns = [
    path("", GeoNationManifestView.as_view(), name="manifest"),
    path("agent/", GeoNationAgentView.as_view(), name="agent-view"),
    # path("agent", GeoNationAgentView.as_view(), name="agent-view"),
]
