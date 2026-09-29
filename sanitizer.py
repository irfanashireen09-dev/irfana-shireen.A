from io import BytesIO
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt

from fpdf import FPDF


def _split_sections(text: str):
    return [line.strip() for line in text.splitlines() if line.strip()]


def format_txt(text: str) -> bytes:
    return text.encode("utf-8")


def format_docx(
    text: str,
    doc_type: str,
    branding: str = "LegalEase"
) -> bytes:

    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    #