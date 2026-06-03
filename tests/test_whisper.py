import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.whisper.transcriber import WhisperManager

class TestWhisperManager(unittest.TestCase):
    """Tests the local WhisperManager class, including lazy initialization and device selection."""

    @patch("app.whisper.transcriber.WhisperModel")
    @patch("app.whisper.transcriber.static_ffmpeg")
    @patch("app.whisper.transcriber.torch")
    def test_whisper_manager_init_cpu(self, mock_torch, mock_ffmpeg, mock_whisper_model) -> None:
        """Verifies that WhisperManager correctly falls back to CPU when CUDA is not available."""
        mock_torch.cuda.is_available.return_value = False
        
        manager = WhisperManager()
        manager.initialize()
        
        # Verify ffmpeg was registered
        mock_ffmpeg.add_paths.assert_called_once()
        
        # Verify correct device and compute type
        self.assertEqual(manager.device, "cpu")
        self.assertEqual(manager.compute_type, "int8")
        
        # Verify WhisperModel was instantiated with the correct arguments
        mock_whisper_model.assert_called_once()
        args, kwargs = mock_whisper_model.call_args
        self.assertEqual(kwargs["device"], "cpu")
        self.assertEqual(kwargs["compute_type"], "int8")

    @patch("app.whisper.transcriber.WhisperModel")
    @patch("app.whisper.transcriber.static_ffmpeg")
    @patch("app.whisper.transcriber.torch")
    def test_whisper_manager_init_cuda(self, mock_torch, mock_ffmpeg, mock_whisper_model) -> None:
        """Verifies that WhisperManager loads with GPU acceleration when CUDA is available."""
        mock_torch.cuda.is_available.return_value = True
        
        manager = WhisperManager()
        manager.initialize()
        
        self.assertEqual(manager.device, "cuda")
        self.assertEqual(manager.compute_type, "float16")
        
        # Verify WhisperModel was instantiated with the correct arguments
        mock_whisper_model.assert_called_once()
        args, kwargs = mock_whisper_model.call_args
        self.assertEqual(kwargs["device"], "cuda")
        self.assertEqual(kwargs["compute_type"], "float16")

    @patch("app.whisper.transcriber.WhisperModel")
    @patch("app.whisper.transcriber.static_ffmpeg")
    def test_whisper_manager_transcribe(self, mock_ffmpeg, mock_whisper_model) -> None:
        """Verifies that transcription correctly calls underlying WhisperModel transcribe method."""
        # Setup mocks
        mock_model_instance = MagicMock()
        mock_segment = MagicMock()
        mock_segment.text = "Hello world from Whisper."
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99
        mock_model_instance.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_model.return_value = mock_model_instance

        manager = WhisperManager()
        result = manager.transcribe("fake_audio_path.wav", language="en")
        
        self.assertEqual(result, "Hello world from Whisper.")
        mock_model_instance.transcribe.assert_called_once_with(
            "fake_audio_path.wav",
            beam_size=5,
            language="en"
        )


class TestWhisperEndpoints(unittest.TestCase):
    """Tests the Speech-to-Text API endpoints on the FastAPI application."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("app.main.whisper_manager")
    @patch("app.main.settings")
    def test_transcription_endpoint_success(self, mock_settings, mock_whisper_manager) -> None:
        """Verifies that the /v1/audio/transcriptions endpoint transcribes files correctly."""
        mock_settings.ENABLE_STT = True
        mock_whisper_manager.transcribe.return_value = "This is a successful transcription test."
        
        # Send fake audio file
        fake_file_content = b"fake audio binary data"
        response = self.client.post(
            "/v1/audio/transcriptions",
            files={"file": ("test.wav", fake_file_content, "audio/wav")},
            data={"language": "en"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"text": "This is a successful transcription test."})
        mock_whisper_manager.transcribe.assert_called_once()

    @patch("app.main.settings")
    def test_transcription_endpoint_disabled(self, mock_settings) -> None:
        """Verifies that the endpoint returns a 400 error when STT is disabled."""
        mock_settings.ENABLE_STT = False
        
        fake_file_content = b"fake audio binary data"
        response = self.client.post(
            "/v1/audio/transcriptions",
            files={"file": ("test.wav", fake_file_content, "audio/wav")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("disabled", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
