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

            ✅ This part makes Telex display a readable message
            response_message = f"{query} is located in {country}."

            info = response.json()[0]
            result = {
                "response": response_message,
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

