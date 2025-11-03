import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

logger = logging.getLogger("agent")

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            body = request.body.decode("utf-8")
        except Exception:
            body = "<unreadable>"

        log_data = {
            "timestamp": str(now()),
            "method": request.method,
            "path": request.get_full_path(),
            "headers": dict(request.headers),
            "body": body,
        }

        logger.info(f"=== Incoming Request ===\n{json.dumps(log_data, indent=2)}")
        return None

    def process_response(self, request, response):
        try:
            response_body = (
                response.content.decode("utf-8")
                if hasattr(response, "content") else str(response)
            )
        except Exception:
            response_body = "<unreadable>"

        logger.info(
            f"=== Outgoing Response ===\n"
            f"Status: {response.status_code}\n"
            f"Body: {response_body[:500]}"
        )
        return response
