import httpx
from app.config.settings import settings
from app.core.logging import logger

class OpenWebUIManager:
    """Manages integration checks for the OpenWebUI application."""

    def __init__(self) -> None:
        self.port = settings.OPENWEBUI_PORT
        self.url = f"http://localhost:{self.port}"

    def is_healthy(self) -> bool:
        """Pings the OpenWebUI port to see if the interface is accessible."""
        try:
            # OpenWebUI exposes a heartbeat/health or general HTML return on root
            response = httpx.get(self.url, timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def get_web_url(self) -> str:
        """Returns the browser-accessible URL for the OpenWebUI dashboard."""
        return self.url
