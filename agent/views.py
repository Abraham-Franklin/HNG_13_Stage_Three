from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
# Create your views here.
class GeoNationManifestView(APIView):
    """
    Telex Agent manifest endpoint — describes your agent to Telex.im.
    """

    def get(self, request):
        data = {
            "name": "GeoNation",
            "description": "GeoNation helps you identify the country a town or city belongs to.",
            "type": "A2A",
            "version": "1.0.0",
            "author": "Okumbor Franklin",
            "endpoints": {
                "primary": "https://abrahamfranklinao.pythonanywhere.com/agent/",
            },
            "tags": ["geolocation", "country lookup", "maps", "OpenStreetMap"]
        }
        return Response(data, status=status.HTTP_200_OK)


class GeoNationAgentView(APIView):
    """
    A2A-compatible endpoint for Telex.im.
    Receives JSON payloads with {method, params, id}
    and returns the corresponding country of a given city/town.
    """

    def post(self, request):
        try:
            method = request.data.get("method")
            params = request.data.get("params", {})
            query = params.get("query")

            if not query:
                return Response(
                    {"error": "Missing 'query' parameter"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
            headers = {"User-Agent": "GeoNation-Agent/1.0"}
            res = requests.get(url, headers=headers)

            if res.status_code != 200 or not res.json():
                return Response(
                    {"error": f"Could not find country for '{query}'"},
                    status=status.HTTP_404_NOT_FOUND
                )

            data = res.json()[0]
            display_name = data.get("display_name", "")
            country = display_name.split(",")[-1].strip()

            result = {
                "place": query,
                "country": country,
                "lat": data.get("lat"),
                "lon": data.get("lon"),
            }

            return Response(
                {"result": result, "id": request.data.get("id")},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

