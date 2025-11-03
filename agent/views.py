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


    def post(self, request):
        try:
            # Extract query
            method = request.data.get("method")
            params = request.data.get("params", {})
            query = params.get("query") or request.data.get("query") or request.data.get("message")

            if not query:
                return Response(
                    {"message": "Please provide the name of a city or town you'd like to know the country for!"},
                    status=status.HTTP_200_OK
                )

            # Query OpenStreetMap
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
            headers = {"User-Agent": "GeoNation-Agent/1.0"}
            res = requests.get(url, headers=headers)

            if res.status_code != 200 or not res.json():
                return Response(
                    {"message": f"Sorry, I couldn’t find the country for '{query}'."},
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

            # Telex expects a simple human-readable message
            response_text = f"{query} is located in {country}. 🌍 (Lat: {data.get('lat')}, Lon: {data.get('lon')})"

            return Response(
                {"result": result, "message": response_text, "id": request.data.get("id")},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def get(self, request):
    #     data = {
    #         "name": "GeoNation",
    #         "description": "GeoNation helps you identify the country a town or city belongs to.",
    #         "type": "A2A",
    #         "version": "1.0.0",
    #         "author": "Okumbor Franklin",
    #         "endpoints": {
    #             "primary": "https://abrahamfranklinao.pythonanywhere.com/agent/",
    #         },
    #         "tags": ["geolocation", "country lookup", "maps", "OpenStreetMap"]
    #     }
    #     return Response(data, status=status.HTTP_200_OK)


# class GeoNationAgentView(APIView):
#     """
#     A2A-compatible endpoint for Telex.im.
#     Receives JSON payloads with {method, params, id}
#     and returns the corresponding country of a given city/town.
#     """

#     def post(self, request):
#         try:
#             method = request.data.get("method")
#             params = request.data.get("params", {})
#             query = params.get("query")

#             if not query:
#                 return Response(
#                     {"error": "Missing 'query' parameter"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
#             headers = {"User-Agent": "GeoNation-Agent/1.0"}
#             res = requests.get(url, headers=headers)

#             if res.status_code != 200 or not res.json():
#                 return Response(
#                     {"error": f"Could not find country for '{query}'"},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             data = res.json()[0]
#             display_name = data.get("display_name", "")
#             country = display_name.split(",")[-1].strip()

#             result = {
#                 "place": query,
#                 "country": country,
#                 "lat": data.get("lat"),
#                 "lon": data.get("lon"),
#             }

#             return Response(
#                 {"result": result, "id": request.data.get("id")},
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







class GeoNationAgentView(APIView):
    def post(self, request):
        data = request.data

        # Accept both Telex and JSON-RPC formats
        query = (
            data.get("params", {}).get("query") or
            data.get("query") or
            data.get("message")
        )

        if not query:
            return Response(
                {"error": "No query provided. Include 'query' or 'message'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call Nominatim API
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {"q": query, "format": "json", "limit": 1}
            # response = requests.get(url, params=params)
            headers = {
                "User-Agent": "GeoNation/1.0 (okumborfranklin@gmail.com)"  # must include email or app name
            }
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json"},
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            results = response.json()

            if not results:
                return Response({"error": f"Could not find location '{query}'."},
                                status=status.HTTP_404_NOT_FOUND)

            location = results[0]
            result = {
                "place": query,
                "country": location.get("display_name").split(",")[-1].strip(),
                "lat": location.get("lat"),
                "lon": location.get("lon")
            }

            # Standardized response for both Telex & manual API
            return Response(
                {"result": result, "id": data.get("id", "1")},
                status=status.HTTP_200_OK
            )

        except requests.RequestException:
            return Response(
                {"error": "Failed to fetch data from OpenStreetMap."},
                status=status.HTTP_502_BAD_GATEWAY
            )