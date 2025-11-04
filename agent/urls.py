# from django.urls import path
# from .views import RootView, GeoNationAgentAPIView

# urlpatterns = [
#     path("", RootView.as_view(), name="root"),
#     path("agent/", GeoNationAgentAPIView.as_view(), name="agent"),
# ]


# from django.urls import path
from .views import RootView, GeoNationAgentAPIView

urlpatterns = [
    path("", RootView.as_view(), name="root"),
    path("agent/", GeoNationAgentAPIView.as_view(), name="agent"),
]
