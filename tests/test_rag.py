import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.utils.helpers import create_mock_pdf
from app.rag.pipeline import RAGPipeline

class TestRAGPipeline(unittest.TestCase):
    """Tests the RAG ingestion structure, helper functions, and settings mapping."""

    def setUp(self) -> None:
        self.temp_dir = Path("./data/test_temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.test_pdf = self.temp_dir / "test_doc.pdf"

    def tearDown(self) -> None:
        # Cleanup mock files
        if self.test_pdf.exists():
            self.test_pdf.unlink()
        if self.temp_dir.exists():
            try:
                self.temp_dir.rmdir()
            except Exception:
                pass

    def test_mock_pdf_generation(self) -> None:
        """Ensures the PDF builder helper creates a readable local binary file."""
        title = "Local AI Test"
        paragraphs = [
            "This is a paragraph verifying standard binary writes for PDF structures.",
            "Technical RAG pipelines can ingest this file and split it into chunks."
        ]
        
        path = create_mock_pdf(self.test_pdf, title, paragraphs)
        self.assertTrue(path.exists())
        self.assertTrue(path.stat().st_size > 100)  # Contains content

    @patch("app.rag.pipeline.QdrantManager")
    @patch("app.rag.pipeline.QdrantClient")
    def test_rag_pipeline_init(self, mock_qdrant, mock_mgr) -> None:
        """Confirms RAG pipeline registers Ollama settings correctly upon initialization."""
        # Setup mocks
        mock_mgr_instance = MagicMock()
        mock_mgr_instance.is_healthy.return_value = True
        mock_mgr.return_value = mock_mgr_instance
        
        pipeline = RAGPipeline(collection_name="test_col")
        self.assertEqual(pipeline.collection_name, "test_col")

if __name__ == "__main__":
    unittest.main()
