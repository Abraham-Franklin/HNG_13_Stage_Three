import json
import logging
import requests
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Use the "agent" logger defined in settings.py
# logger = logging.getLogger("agent")


# ✅ Configure logging for both console (Railway logs) and file
logger = logging.getLogger("agent")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("geonation.log"),  # saves logs to file in container
        logging.StreamHandler()  # sends logs to console → visible in Railway dashboard
    ]
)


class GeoNationManifestView(APIView):
    """
    Telex Agent manifest endpoint — describes your agent to Telex.im.
    """

    def post(self, request):
        logger.info("=== Incoming Request to / (Manifest) ===")
        logger.info(f"Timestamp: {now()}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body: {json.dumps(request.data, indent=2)}")

        try:
            # Extract the query from different possible formats
            method = request.data.get("method")
            params = request.data.get("params", {})
            query = params.get("query") or request.data.get("query") or request.data.get("message")

            if not query:
                logger.warning("No query provided in request.")
                return Response(
                    {"message": "Please provide the name of a city or town you'd like to know the country for!"},
                    status=status.HTTP_200_OK
                )

            # Query OpenStreetMap Nominatim API
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
            headers = {"User-Agent": "GeoNation-Agent/1.0 (okumborfranklin@gmail.com)"}
            res = requests.get(url, headers=headers, timeout=10)

            logger.info(f"Nominatim Request URL: {res.url}")
            logger.info(f"Nominatim Response Code: {res.status_code}")
            logger.debug(f"Nominatim Raw Response: {res.text[:400]}")

            if res.status_code != 200 or not res.json():
                logger.warning(f"No results found for '{query}'.")
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

            response_text = f"{query} is located in {country}. 🌍 (Lat: {data.get('lat')}, Lon: {data.get('lon')})"
            response_data = {"result": result, "message": response_text, "id": request.data.get("id")}

            logger.info(f"Response to Telex: {json.dumps(response_data, indent=2)}")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error processing request in Manifest view")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GeoNationAgentView(APIView):
    """
    The actual GeoNation agent logic endpoint — receives Telex A2A POST calls.
    """

    def post(self, request):
        logger.info("=== Incoming Request to /agent/ ===")
        logger.info(f"Timestamp: {now()}")
        logger.info(f"Headers: {dict(request.headers)}")
        try:
            body_str = request.body.decode("utf-8")
            logger.debug(f"Raw Body: {body_str}")
        except Exception:
            body_str = "<unreadable>"
        logger.info(f"Parsed Body: {json.dumps(request.data, indent=2)}")

        data = request.data
        query = (
            data.get("params", {}).get("query")
            or data.get("query")
            or data.get("message")
        )

        if not query:
            logger.warning("No query provided in agent request.")
            return Response(
                {"error": "No query provided. Include 'query' or 'message'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Query OpenStreetMap Nominatim API
            headers = {"User-Agent": "GeoNation/1.0 (okumborfranklin@gmail.com)"}
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json"},
                headers=headers,
                timeout=10
            )

            logger.info(f"Nominatim URL: {response.url}")
            logger.info(f"Nominatim Status: {response.status_code}")
            logger.debug(f"Nominatim Response: {response.text[:400]}")

            response.raise_for_status()
            results = response.json()

            if not results:
                logger.warning(f"No results found for '{query}'.")
                return Response(
                    {"error": f"Could not find location '{query}'."},
                    status=status.HTTP_404_NOT_FOUND
                )

            location = results[0]
            result = {
                "place": query,
                "country": location.get("display_name").split(",")[-1].strip(),
                "lat": location.get("lat"),
                "lon": location.get("lon")
            }

            response_payload = {"result": result, "id": data.get("id", "1")}
            logger.info(f"Responding to Telex with: {json.dumps(response_payload, indent=2)}")

            return Response(response_payload, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            logger.exception("Error fetching data from OpenStreetMap.")
            return Response(
                {"error": "Failed to fetch data from OpenStreetMap."},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.exception("Unexpected error in GeoNationAgentView.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










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