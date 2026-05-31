"""build_tdd_pdf.py — Render docs/TDD_report.md into docs/TDD_report.pdf.

A lightweight Markdown-to-PDF pass using PyMuPDF (fitz). It is intentionally
simple: it honours headings, code fences and bullet/paragraph wrapping — enough
for a clean, readable technical report. Build-time tool, not game runtime.

    python tools/build_tdd_pdf.py
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "TDD_report.md"
OUT = ROOT / "docs" / "TDD_report.pdf"

PAGE_W, PAGE_H = 595, 842  # A4 in points
MARGIN = 56
LINE_H = 15


def _wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    """Greedy word-wrap `text` to fit `max_w` points at the given font/size."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if fitz.get_text_length(trial, fontname=font, fontsize=size) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    lines.append(current)
    return lines or [""]


def _style(line: str) -> tuple[str, float, str, float]:
    """Map a Markdown line to (text, fontsize, fontname, top_gap)."""
    if line.startswith("### "):
        return line[4:], 12.5, "hebo", 8
    if line.startswith("## "):
        return line[3:], 15, "hebo", 12
    if line.startswith("# "):
        return line[2:], 20, "hebo", 14
    if line.startswith(("- ", "* ")):
        return "•  " + line[2:], 10.5, "helv", 2
    return line, 10.5, "helv", 2


class _Writer:
    """Tracks the cursor across pages and emits wrapped lines."""

    def __init__(self, doc: fitz.Document) -> None:
        self.doc = doc
        self.page = doc.new_page(width=PAGE_W, height=PAGE_H)
        self.y = MARGIN

    def _newline(self, height: float) -> None:
        """Advance the cursor, starting a new page when the bottom is reached."""
        if self.y + height > PAGE_H - MARGIN:
            self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)
            self.y = MARGIN

    def emit(self, text: str, size: float, font: str, gap: float, mono: bool) -> None:
        """Write one logical line (wrapped) at the current cursor position."""
        self.y += gap
        face = "cour" if mono else font
        max_w = PAGE_W - 2 * MARGIN
        for piece in _wrap(text, face, size, max_w) if not mono else [text]:
            self._newline(LINE_H)
            self.page.insert_text((MARGIN, self.y), piece, fontsize=size, fontname=face)
            self.y += LINE_H


def main() -> None:
    """Convert the Markdown report to a paginated PDF."""
    doc = fitz.open()
    writer = _Writer(doc)
    in_code = False
    for raw in SRC.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            writer.emit(raw, 9, "cour", 0, mono=True)
            continue
        if not raw.strip():
            writer.y += 6
            continue
        text, size, font, gap = _style(raw)
        writer.emit(text, size, font, gap, mono=False)
    doc.save(OUT)
    doc.close()
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
