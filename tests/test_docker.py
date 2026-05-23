import unittest
from unittest.mock import patch, MagicMock
from app.docker.orchestrator import DockerOrchestrator

class TestDockerOrchestrator(unittest.TestCase):
    """Tests the container spec generation, network adapters, and environment injection."""

    def test_ollama_url_mapping(self) -> None:
        """Verifies that localhost addresses are accurately rewritten for container consumption."""
        orc = DockerOrchestrator()
        
        # Test default http://localhost:11434 rewriting
        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            docker_url = orc._get_ollama_docker_url()
            self.assertEqual(docker_url, "http://host.docker.internal:11434")
            
        # Test 127.0.0.1 mapping
        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.OLLAMA_HOST = "http://127.0.0.1:11434"
            docker_url = orc._get_ollama_docker_url()
            self.assertEqual(docker_url, "http://host.docker.internal:11434")

        # Test external IP mapping (should remain unchanged)
        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.OLLAMA_HOST = "http://192.168.1.50:11434"
            docker_url = orc._get_ollama_docker_url()
            self.assertEqual(docker_url, "http://192.168.1.50:11434")

    def test_services_definitions(self) -> None:
        """Confirms container specifications contain correct volume binds and target ports."""
        orc = DockerOrchestrator()
        specs = orc.get_services_definitions()
        
        # Check we have exactly 4 defined containers
        self.assertEqual(len(specs), 4)
        
        names = [spec["name"] for spec in specs]
        self.assertIn("qdrant", names)
        self.assertIn("open-webui", names)
        self.assertIn("xtts", names)
        self.assertIn("n8n", names)
        
        # Verify OpenWebUI contains the OLLAMA_BASE_URL env setting
        openwebui_spec = next(spec for spec in specs if spec["name"] == "open-webui")
        self.assertIn("OLLAMA_BASE_URL", openwebui_spec["environment"])
        self.assertIn("host.docker.internal", openwebui_spec["environment"]["OLLAMA_BASE_URL"])

if __name__ == "__main__":
    unittest.main()
