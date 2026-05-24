import unittest
from unittest.mock import patch, MagicMock
from app.core.system import detect_gpu, generate_system_report, SystemReport, GPUInfo

class TestSystemModule(unittest.TestCase):
    """Tests the system resource verification checks and GPU detection logic."""

    @patch("subprocess.run")
    def test_detect_gpu_nvidia_success(self, mock_run) -> None:
        """Tests successful parsing of nvidia-smi command output."""
        # Mock successful nvidia-smi execution returning a standard Geforce RTX 3080
        mock_response = MagicMock()
        mock_response.stdout = "NVIDIA GeForce RTX 3080, 10240, 528.49\n"
        mock_response.return_code = 0
        mock_run.return_value = mock_response

        gpu = detect_gpu()
        self.assertTrue(gpu.detected)
        self.assertEqual(gpu.name, "NVIDIA GeForce RTX 3080")
        self.assertEqual(gpu.vram_mb, 10240)
        self.assertEqual(gpu.driver_version, "528.49")

    @patch("subprocess.run")
    def test_detect_gpu_nvidia_failed(self, mock_run) -> None:
        """Tests GPU detection when nvidia-smi is unavailable or returns an error."""
        mock_run.side_effect = FileNotFoundError("No command found")
        
        gpu = detect_gpu()
        self.assertFalse(gpu.detected)
        self.assertIsNone(gpu.name)
        self.assertIsNone(gpu.vram_mb)

    @patch("subprocess.run")
    @patch("platform.system")
    @patch("psutil.virtual_memory")
    def test_detect_gpu_macos_success(self, mock_vm, mock_system, mock_run) -> None:
        """Tests successful parsing of macOS system_profiler GPU information."""
        mock_system.return_value = "Darwin"
        
        # Mock virtual memory total to be 8GB (8192 MB)
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024 * 1024 * 1024
        mock_vm.return_value = mock_mem
        
        # Second call (system_profiler SPDisplaysDataType) returns chipset model
        mock_run_profile = MagicMock()
        mock_run_profile.stdout = "Graphics/Displays:\n\n    Apple M1:\n\n      Chipset Model: Apple M1\n      Type: GPU\n"
        mock_run_profile.return_code = 0
        
        # subprocess.run is called twice: first for nvidia-smi, then for system_profiler
        mock_run.side_effect = [FileNotFoundError("nvidia-smi not found"), mock_run_profile]
        
        gpu = detect_gpu()
        self.assertTrue(gpu.detected)
        self.assertEqual(gpu.name, "Apple M1")
        self.assertEqual(gpu.vram_mb, 8192)
        self.assertEqual(gpu.driver_version, "Metal Support")

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
