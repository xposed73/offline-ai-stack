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

        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.ENABLE_TTS = True
            mock_settings.APP_LANGUAGE = "en"
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_GRPC_PORT = 6334
            mock_settings.OPENWEBUI_PORT = 3000
            mock_settings.KOKORO_PORT = 8880
            mock_settings.KOKORO_IMAGE = "ghcr.io/remsky/kokoro-fastapi-gpu:latest"
            mock_settings.KOKORO_VOICE = "af_sky"
            mock_settings.KOKORO_MODEL = "kokoro"
            mock_settings.N8N_PORT = 5678
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.qdrant_path = "/tmp/qdrant"
            mock_settings.openwebui_path = "/tmp/openwebui"
            mock_settings.kokoro_path = "/tmp/kokoro"
            mock_settings.n8n_path = "/tmp/n8n"
            mock_settings.ENABLE_STT = True
            mock_settings.APP_PORT = 8000
            mock_settings.WHISPER_MODEL = "base"

            specs = orc.get_services_definitions()
            self.assertEqual(len(specs), 4)
            names = [spec["name"] for spec in specs]
            self.assertIn("qdrant", names)
            self.assertIn("open-webui", names)
            self.assertIn("kokoro", names)
            self.assertIn("n8n", names)

            openwebui_spec = next(spec for spec in specs if spec["name"] == "open-webui")
            self.assertIn("OLLAMA_BASE_URL", openwebui_spec["environment"])
            self.assertIn("AUDIO_TTS_ENGINE", openwebui_spec["environment"])
            self.assertEqual(openwebui_spec["environment"]["AUDIO_TTS_OPENAI_API_BASE_URL"], "http://kokoro:8881/v1")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_TTS_VOICE"], "af_sky")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_TTS_MODEL"], "kokoro")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_STT_ENGINE"], "openai")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_STT_OPENAI_API_BASE_URL"], "http://host.docker.internal:8000/v1")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_STT_OPENAI_API_KEY"], "offline-ai-stack")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_STT_MODEL"], "base")

        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.ENABLE_TTS = True
            mock_settings.APP_LANGUAGE = "de"
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_GRPC_PORT = 6334
            mock_settings.OPENWEBUI_PORT = 3000
            mock_settings.KOKORO_PORT = 8880
            mock_settings.KOKORO_IMAGE = "ghcr.io/remsky/kokoro-fastapi-cpu:v0.3.0"
            mock_settings.KOKORO_VOICE = "af_sky"
            mock_settings.KOKORO_MODEL = "kokoro"
            mock_settings.N8N_PORT = 5678
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.qdrant_path = "/tmp/qdrant"
            mock_settings.openwebui_path = "/tmp/openwebui"
            mock_settings.kokoro_path = "/tmp/kokoro"
            mock_settings.n8n_path = "/tmp/n8n"
            mock_settings.ENABLE_STT = False

            specs = orc.get_services_definitions()
            openwebui_spec = next(spec for spec in specs if spec["name"] == "open-webui")
            self.assertEqual(openwebui_spec["environment"]["AUDIO_TTS_OPENAI_API_BASE_URL"], "http://kokoro:8881/v1")
            self.assertNotIn("AUDIO_STT_ENGINE", openwebui_spec["environment"])

        with patch("app.docker.orchestrator.settings") as mock_settings:
            mock_settings.ENABLE_TTS = False
            mock_settings.APP_LANGUAGE = "en"
            mock_settings.QDRANT_PORT = 6333
            mock_settings.QDRANT_GRPC_PORT = 6334
            mock_settings.OPENWEBUI_PORT = 3000
            mock_settings.N8N_PORT = 5678
            mock_settings.OLLAMA_HOST = "http://localhost:11434"
            mock_settings.qdrant_path = "/tmp/qdrant"
            mock_settings.openwebui_path = "/tmp/openwebui"
            mock_settings.n8n_path = "/tmp/n8n"
            mock_settings.ENABLE_STT = False

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
            self.assertNotIn("AUDIO_STT_ENGINE", openwebui_spec["environment"])

if __name__ == "__main__":
    unittest.main()
