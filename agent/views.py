import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class RootView(APIView):
    """
    Root endpoint — provides service metadata.
    """
    def get(self, request):
        logger.info("=== Root Endpoint Accessed ===")
        return Response({
            "name": "GeoNation Agent",
            "version": "1.0.1",
            "description": "Receives a location name and returns the country it belongs to. Compatible with A2A JSON-RPC format.",
            "author": "Okumbor Franklin",
            "repository": "https://github.com/yourusername/geonation-agent"
        }, status=status.HTTP_200_OK)


class GeoNationAgentAPIView(APIView):
    """
    A2A-compatible Agent endpoint that handles both JSON-RPC and Telex payloads.
    """

    def post(self, request):
        logger.info("=== Incoming A2A POST Request ===")

        data = request.data
        logger.debug(f"Raw incoming data: {data}")

        # Try to extract query in a flexible manner
        query = None
        rpc_id = None

        try:
            if isinstance(data, dict):
                rpc_id = data.get("id")

                # JSON-RPC structured request
                if "params" in data and isinstance(data["params"], dict):
                    query = data["params"].get("query")

                # Direct query field
                elif "query" in data:
                    query = data.get("query")

                # Telex-style A2A format (wrapped inside data)
                elif "data" in data and isinstance(data["data"], dict):
                    query = data["data"].get("query")
        except Exception as parse_err:
            logger.error(f"Error parsing incoming data: {parse_err}")
            return Response({
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid JSON structure"},
                "id": rpc_id
            }, status=status.HTTP_200_OK)

        if not query:
            logger.warning("Missing 'query' parameter in request")
            return Response({
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Missing 'query' parameter"},
                "id": rpc_id
            }, status=status.HTTP_200_OK)

        # Fetch country data from OpenStreetMap Nominatim
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/search?format=json&q={query}",
                headers={"User-Agent": "GeoNationAgent/1.0"}
            )
            logger.info(f"Nominatim response code: {response.status_code}")

            if response.status_code != 200 or not response.json():
                logger.warning(f"No result found for query: {query}")
                return Response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32004, "message": f"No country found for '{query}'"},
                    "id": rpc_id
                }, status=status.HTTP_200_OK)

            info = response.json()[0]
            result = {
                "query": query,
                "country": info.get("display_name", "").split(",")[-1].strip(),
                "latitude": info.get("lat"),
                "longitude": info.get("lon")
            }

            logger.info(f"Resolved '{query}' → {result['country']}")
            return Response({
                "jsonrpc": "2.0",
                "result": result,
                "id": rpc_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error during API call")
            return Response({
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": f"Server error: {str(e)}"},
                "id": rpc_id
            }, status=status.HTTP_200_OK)

















# import json
# import logging
# import requests
# from django.http import JsonResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# logger = logging.getLogger(__name__)

# class RootView(APIView):
#     """
#     Root endpoint — provides service metadata.
#     """
#     def get(self, request):
#         logger.info("=== Root Endpoint Accessed ===")
#         return Response({
#             "name": "GeoNation Agent",
#             "version": "1.0.0",
#             "description": "Receives a location name and returns the country it belongs to.",
#             "author": "Okumbor Franklin",
#             "repository": "https://github.com/yourusername/geonation-agent"
#         }, status=status.HTTP_200_OK)


# class GeoNationAgentAPIView(APIView):
#     """
#     A2A-compatible Agent endpoint that receives POST requests
#     and returns country information for a given city/town name.
#     """

#     def post(self, request):
#         logger.info("=== Incoming A2A POST Request ===")

#         try:
#             # Parse request body (ensure it's JSON-RPC 2.0 formatted)
#             data = request.data
#             logger.debug(f"Raw incoming data: {data}")

#             # Validate the A2A JSON-RPC structure
#             if not data or "method" not in data or "params" not in data:
#                 logger.warning("Invalid request format")
#                 return Response({
#                     "jsonrpc": "2.0",
#                     "error": {
#                         "code": -32600,
#                         "message": "Invalid Request Format. Expected JSON-RPC 2.0"
#                     },
#                     "id": data.get("id") if isinstance(data, dict) else None
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Handle getCountry method
#             if data["method"] != "getCountry":
#                 logger.warning("Unsupported method called")
#                 return Response({
#                     "jsonrpc": "2.0",
#                     "error": {
#                         "code": -32601,
#                         "message": f"Unsupported method: {data['method']}"
#                     },
#                     "id": data.get("id")
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             query = data["params"].get("query")
#             if not query:
#                 logger.warning("Missing query parameter")
#                 return Response({
#                     "jsonrpc": "2.0",
#                     "error": {
#                         "code": -32602,
#                         "message": "Missing required parameter: query"
#                     },
#                     "id": data.get("id")
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Fetch data from external API
#             url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
#             response = requests.get(url, headers={"User-Agent": "GeoNationAgent/1.0"})
#             logger.info(f"Fetched data from Nominatim: {response.status_code}")

#             if response.status_code != 200 or not response.json():
#                 logger.error(f"No data found for {query}")
#                 return Response({
#                     "jsonrpc": "2.0",
#                     "error": {
#                         "code": -32004,
#                         "message": f"Could not find country for '{query}'"
#                     },
#                     "id": data.get("id")
#                 }, status=status.HTTP_404_NOT_FOUND)

#             result = response.json()[0]
#             country = result.get("display_name", "").split(",")[-1].strip()
#             lat = result.get("lat")
#             lon = result.get("lon")

#             output = {
#                 "query": query,
#                 "country": country,
#                 "latitude": lat,
#                 "longitude": lon
#             }

#             logger.info(f"Resolved {query} → {country}")
#             return Response({
#                 "jsonrpc": "2.0",
#                 "result": output,
#                 "id": data.get("id")
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.exception("Unexpected error occurred")
#             return Response({
#                 "jsonrpc": "2.0",
#                 "error": {
#                     "code": -32000,
#                     "message": f"Server error: {str(e)}"
#                 },
#                 "id": None
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
