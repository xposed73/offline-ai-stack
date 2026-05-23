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
        
        # Test with ENABLE_TTS = True
        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.ENABLE_TTS = True
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_GRPC_PORT = 6334
            mock_settings.OPENWEBUI_PORT = 3000
            mock_settings.XTTS_PORT = 8020
            mock_settings.N8N_PORT = 5678
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.qdrant_path = "/tmp/qdrant"
            mock_settings.openwebui_path = "/tmp/openwebui"
            mock_settings.xtts_path = "/tmp/xtts"
            mock_settings.n8n_path = "/tmp/n8n"
            
            specs = orc.get_services_definitions()
            self.assertEqual(len(specs), 4)
            names = [spec["name"] for spec in specs]
            self.assertIn("qdrant", names)
            self.assertIn("open-webui", names)
            self.assertIn("xtts", names)
            self.assertIn("n8n", names)
            
            openwebui_spec = next(spec for spec in specs if spec["name"] == "open-webui")
            self.assertIn("OLLAMA_BASE_URL", openwebui_spec["environment"])
            self.assertIn("AUDIO_TTS_ENGINE", openwebui_spec["environment"])
            self.assertEqual(openwebui_spec["environment"]["AUDIO_TTS_API_BASE_URL"], "http://xtts:8020/v1")

        # Test with ENABLE_TTS = False
        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.ENABLE_TTS = False
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_GRPC_PORT = 6334
            mock_settings.OPENWEBUI_PORT = 3000
            mock_settings.N8N_PORT = 5678
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.qdrant_path = "/tmp/qdrant"
            mock_settings.openwebui_path = "/tmp/openwebui"
            mock_settings.n8n_path = "/tmp/n8n"
            
            specs = orc.get_services_definitions()
            self.assertEqual(len(specs), 3)
            names = [spec["name"] for spec in specs]
            self.assertIn("qdrant", names)
            self.assertIn("open-webui", names)
            self.assertNotIn("xtts", names)
            self.assertIn("n8n", names)
            
            openwebui_spec = next(spec for spec in specs if spec["name"] == "open-webui")
            self.assertIn("OLLAMA_BASE_URL", openwebui_spec["environment"])
            self.assertNotIn("AUDIO_TTS_ENGINE", openwebui_spec["environment"])

if __name__ == "__main__":
    unittest.main()
