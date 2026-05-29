import httpx
from app.config.settings import settings
from app.core.logging import logger

class N8NManager:
    """Manages integration checks and webhook hooks for the n8n automation server."""

    def __init__(self) -> None:
        self.port = settings.N8N_PORT
        self.url = f"http://localhost:{self.port}"

    def is_healthy(self) -> bool:
        """Pings the n8n health endpoint (standard /healthz) to check service health."""
        try:
            # n8n exposes a standard /healthz or /rest/health endpoint
            response = httpx.get(f"{self.url}/healthz", timeout=2.0)
            return response.status_code == 200 or response.json().get("status") == "ok"
        except Exception:
            # Fallback to general port ping
            try:
                res = httpx.get(self.url, timeout=2.0, follow_redirects=True)
                return res.status_code == 200
            except Exception:
                return False

    def get_web_url(self) -> str:
        """Returns the browser-accessible URL for the n8n dashboard."""
        return self.url
