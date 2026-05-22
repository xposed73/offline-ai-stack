import os
from pathlib import Path
from typing import Dict, Any, Union
import yaml
from app.core.logging import logger

def format_bytes(size_in_bytes: Union[int, float]) -> str:
    """Formats raw bytes to a human-readable size (e.g. MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Safely loads a YAML configuration file."""
    if not file_path.exists():
        logger.warning(f"YAML file not found at {file_path}. Returning empty dictionary.")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Error loading YAML file {file_path}: {e}")
        return {}

def create_mock_pdf(output_path: Path, title: str, paragraphs: list[str]) -> Path:
    """Generates a simple, readable PDF file containing sample text for ingestion tests.
    
    This avoids requiring a heavy external library like ReportLab or FPDF during setup.
    We build a basic PDF 1.4 structured binary file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # PDF generation logic: standard static PDF objects
    content = ""
    for p in paragraphs:
        content += f"{p}\n\n"
        
    pdf_template = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        "4 0 obj\n<< /Length {length} >>\nstream\n"
        "BT\n/F1 12 Tf\n70 750 Td\n14 TL\n"
    )
    
    # Convert paragraph lines into PDF text instructions (Tj/T*)
    text_instructions = f"({title}) Tj T*\n"
    for line in paragraphs:
        # Simple escape of parentheses
        line_esc = line.replace("(", "\\(").replace(")", "\\)")
        # Split line if very long to prevent visual overlap
        words = line_esc.split(" ")
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 70:
                text_instructions += f"({' '.join(current_line[:-1])}) Tj T*\n"
                current_line = [word]
        if current_line:
            text_instructions += f"({' '.join(current_line)}) Tj T*\n"
        text_instructions += "T*\n"
        
    text_instructions += "ET\n"
    stream_content = text_instructions.encode("utf-8")
    
    stream_part = pdf_template.format(length=len(stream_content)).encode("utf-8")
    stream_end = b"endstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000282 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
    
    # Calculate exact xref position
    xref_pos = len(stream_part) + len(stream_content) + len("endstream\nendobj\n")
    
    final_pdf_content = stream_part + stream_content + stream_end.replace(b"{xref_pos}", str(xref_pos).encode("utf-8"))
    
    with open(output_path, "wb") as f:
        f.write(final_pdf_content)
        
    logger.debug(f"Mock PDF created successfully at: {output_path}")
    return output_path
