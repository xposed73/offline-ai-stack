import unittest
from unittest.mock import patch, MagicMock
from app.core.system import detect_nvidia_gpu, generate_system_report, SystemReport, GPUInfo

class TestSystemModule(unittest.TestCase):
    """Tests the system resource verification checks and GPU detection logic."""

    @patch("subprocess.run")
    def test_detect_nvidia_gpu_success(self, mock_run) -> None:
        """Tests successful parsing of nvidia-smi command output."""
        # Mock successful nvidia-smi execution returning a standard Geforce RTX 3080
        mock_response = MagicMock()
        mock_response.stdout = "NVIDIA GeForce RTX 3080, 10240, 528.49\n"
        mock_response.return_code = 0
        mock_run.return_value = mock_response

        gpu = detect_nvidia_gpu()
        self.assertTrue(gpu.detected)
        self.assertEqual(gpu.name, "NVIDIA GeForce RTX 3080")
        self.assertEqual(gpu.vram_mb, 10240)
        self.assertEqual(gpu.driver_version, "528.49")

    @patch("subprocess.run")
    def test_detect_nvidia_gpu_failed(self, mock_run) -> None:
        """Tests GPU detection when nvidia-smi is unavailable or returns an error."""
        mock_run.side_effect = FileNotFoundError("No command found")
        
        gpu = detect_nvidia_gpu()
        self.assertFalse(gpu.detected)
        self.assertIsNone(gpu.name)
        self.assertIsNone(gpu.vram_mb)

    @patch("app.core.system.verify_docker")
    @patch("app.core.system.verify_ollama")
    def test_generate_system_report(self, mock_ollama, mock_docker) -> None:
        """Checks if system report compilation runs successfully and flags warnings correctly."""
        mock_docker.return_value = (True, True)  # Installed and running
        mock_ollama.return_value = True          # Running
        
        report = generate_system_report()
        self.assertIsInstance(report, SystemReport)
        self.assertTrue(report.docker_installed)
        self.assertTrue(report.docker_running)
        self.assertTrue(report.ollama_running)
        self.assertIsInstance(report.cpu_count, int)
        self.assertIsInstance(report.ram_gb, float)

if __name__ == "__main__":
    unittest.main()
