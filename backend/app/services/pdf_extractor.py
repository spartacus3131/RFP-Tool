"""
PDF Text Extraction Service using PyMuPDF.

Extracts text from PDFs while preserving page structure for source linking.
"""
import fitz  # PyMuPDF
from dataclasses import dataclass
from typing import Optional


@dataclass
class PDFExtractionResult:
    """Result of PDF text extraction."""
    success: bool
    text: Optional[str] = None
    page_count: int = 0
    error: Optional[str] = None


def extract_text_from_pdf(file_path: str) -> PDFExtractionResult:
    """
    Extract all text from a PDF file.

    Returns text with page markers for source linking:
    --- PAGE 1 ---
    [text from page 1]
    --- PAGE 2 ---
    [text from page 2]
    ...

    Args:
        file_path: Path to the PDF file

    Returns:
        PDFExtractionResult with extracted text and metadata
    """
    try:
        doc = fitz.open(file_path)
        pages_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            # Add page marker for source linking
            pages_text.append(f"\n--- PAGE {page_num + 1} ---\n{text}")

        doc.close()

        full_text = "\n".join(pages_text)

        return PDFExtractionResult(
            success=True,
            text=full_text,
            page_count=len(pages_text),
        )

    except Exception as e:
        return PDFExtractionResult(
            success=False,
            error=str(e),
        )


def extract_text_by_page(file_path: str) -> list[dict]:
    """
    Extract text from each page separately.

    Useful for more granular source linking.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of dicts with {page_number, text, word_count}
    """
    try:
        doc = fitz.open(file_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "word_count": len(text.split()),
            })

        doc.close()
        return pages

    except Exception as e:
        return []


def get_pdf_metadata(file_path: str) -> dict:
    """
    Get PDF metadata (title, author, creation date, etc.)
    """
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        page_count = len(doc)
        doc.close()

        return {
            "page_count": page_count,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "creation_date": metadata.get("creationDate", ""),
        }

    except Exception as e:
        return {"error": str(e)}
