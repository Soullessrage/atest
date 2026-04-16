from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class PdfExportService:
    def __init__(self, target_path: Path):
        self.target_path = target_path

    def export_world_summary(self, world_name: str, summary_text: str) -> None:
        doc = SimpleDocTemplate(str(self.target_path), pagesize=letter)
        story = []
        style = ParagraphStyle(name="Normal", fontSize=11, leading=14)
        story.append(Paragraph(f"<b>{world_name}</b>", style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(summary_text.replace("\n", "<br/>"), style))
        doc.build(story)
