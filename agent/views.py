import logging
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class GeoNationAgentView(APIView):
    """
    Handles requests to retrieve the country of a given city, town, or location name.
    """

    def get(self, request):
        location = request.query_params.get("location")

        if not location:
            logger.warning("No location provided in request.")
            return Response(
                {"error": "Please provide a 'location' query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/search",
                params={"q": location, "format": "json", "addressdetails": 1},
                headers={"User-Agent": "GeoNationAgent/1.0"},
                timeout=10,
            )

            data = response.json()
            if not data:
                logger.info(f"No country found for location: {location}")
                return Response(
                    {"message": f"Could not find a country for '{location}'."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            country = data[0]["address"].get("country", "Unknown")
            logger.info(f"Location '{location}' found in {country}")

            return Response(
                {"location": location, "country": country},
                status=status.HTTP_200_OK,
            )

        except requests.RequestException as e:
            logger.error(f"Error fetching data from Nominatim API: {str(e)}")
            return Response(
                {"error": "Failed to retrieve data from external API."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GeoNationManifestView(APIView):
    """
    Provides metadata about the GeoNation Agent service.
    """

    def get(self, request):
        manifest_data = {
            "name": "GeoNation Agent",
            "version": "1.0.0",
            "description": "Receives a location name and returns the country it belongs to.",
            "author": "Okumbor Franklin",
            "repository": "https://github.com/yourusername/geonation-agent",
        }
        logger.debug("Manifest data served successfully.")
        return Response(manifest_data, status=status.HTTP_200_OK)





# class GeoNationAgentView(APIView):
#     """
#     GeoNation agent logic endpoint — receives Telex A2A POST calls and returns country information.
#     """

#     def get(self, request):
#         """Simple GET endpoint to verify that the agent endpoint is active."""
#         logger.info("Health check request received at /agent/")
#         return Response({"message": "GeoNation Agent is running!"}, status=status.HTTP_200_OK)

#     def post(self, request):
#         logger.info("=== Incoming Request to /agent/ ===")
#         logger.info(f"Timestamp: {now()}")
#         logger.info(f"Headers: {dict(request.headers)}")

#         try:
#             body_str = request.body.decode("utf-8")
#             logger.debug(f"Raw Body: {body_str}")
#         except Exception:
#             body_str = "<unreadable>"

#         logger.info(f"Parsed Body: {json.dumps(request.data, indent=2)}")

#         data = request.data
#         query = (
#             data.get("params", {}).get("query")
#             or data.get("query")
#             or data.get("message")
#         )

#         # Handle Telex A2A structured message format
#         if not query:
#             message = data.get("params", {}).get("message", {})
#             parts = message.get("parts", [])
#             if parts and isinstance(parts, list):
#                 for part in parts:
#                     if part.get("kind") == "text" and "text" in part:
#                         text_value = part["text"].strip()
#                         if text_value.startswith("/geonation_agent"):
#                             query = text_value.replace("/geonation_agent", "").strip()
#                         else:
#                             query = text_value
#                         break

#         if not query:
#             logger.warning("No query provided in agent request.")
#             return Response(
#                 {"error": "No query provided. Include 'query' or 'message'."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # ✅ Query OpenStreetMap API
#             headers = {"User-Agent": "GeoNation/1.0 (contact: okumborfranklin@gmail.com)"}
#             response = requests.get(
#                 "https://nominatim.openstreetmap.org/search",
#                 params={"q": query, "format": "json"},
#                 headers=headers,
#                 timeout=10
#             )

#             logger.info(f"Nominatim URL: {response.url}")
#             logger.info(f"Nominatim Status: {response.status_code}")
#             logger.debug(f"Nominatim Response: {response.text[:400]}")

#             response.raise_for_status()
#             results = response.json()

#             if not results:
#                 logger.warning(f"No results found for '{query}'.")
#                 return Response(
#                     {"error": f"Could not find location '{query}'."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             location = results[0]
#             display_name = location.get("display_name", "")
#             country = display_name.split(",")[-1].strip() if display_name else "Unknown"

#             result = {
#                 "place": query,
#                 "country": country,
#                 "lat": location.get("lat"),
#                 "lon": location.get("lon")
#             }

#             response_payload = {"result": result, "id": data.get("id", "1")}
#             logger.info(f"Responding to Telex with: {json.dumps(response_payload, indent=2)}")

#             return Response(response_payload, status=status.HTTP_200_OK)

#         except requests.RequestException:
#             logger.exception("Error fetching data from OpenStreetMap.")
#             return Response(
#                 {"error": "Failed to fetch data from OpenStreetMap."},
#                 status=status.HTTP_502_BAD_GATEWAY
#             )

#         except Exception as e:
#             logger.exception("Unexpected error in GeoNationAgentView.")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# # Create your views here.
# class GeoNationManifestView(APIView):
#     """
#     Telex Agent manifest endpoint — describes your agent to Telex.im.
#     """


#     def post(self, request):
#         try:
#             # Extract query
#             method = request.data.get("method")
#             params = request.data.get("params", {})
#             query = params.get("query") or request.data.get("query") or request.data.get("message")

#             if not query:
#                 return Response(
#                     {"message": "Please provide the name of a city or town you'd like to know the country for!"},
#                     status=status.HTTP_200_OK
#                 )

#             # Query OpenStreetMap
#             url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
#             headers = {"User-Agent": "GeoNation-Agent/1.0"}
#             res = requests.get(url, headers=headers)

#             if res.status_code != 200 or not res.json():
#                 return Response(
#                     {"message": f"Sorry, I couldn’t find the country for '{query}'."},
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

#             # Telex expects a simple human-readable message
#             response_text = f"{query} is located in {country}. 🌍 (Lat: {data.get('lat')}, Lon: {data.get('lon')})"

#             return Response(
#                 {"result": result, "message": response_text, "id": request.data.get("id")},
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#     # def get(self, request):
#     #     data = {
#     #         "name": "GeoNation",
#     #         "description": "GeoNation helps you identify the country a town or city belongs to.",
#     #         "type": "A2A",
#     #         "version": "1.0.0",
#     #         "author": "Okumbor Franklin",
#     #         "endpoints": {
#     #             "primary": "https://abrahamfranklinao.pythonanywhere.com/agent/",
#     #         },
#     #         "tags": ["geolocation", "country lookup", "maps", "OpenStreetMap"]
#     #     }
#     #     return Response(data, status=status.HTTP_200_OK)


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







# class GeoNationAgentView(APIView):
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