#!/usr/bin/env python3
"""Compose the Wump Institute treatises as paginated PDFs."""

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from library import BOOKS

ROOT = Path(__file__).resolve().parents[1]
EBOOKS = ROOT / "ebooks"

pdfmetrics.registerFont(TTFont("Caslon", "/System/Library/Fonts/Supplemental/BigCaslon.ttf"))
pdfmetrics.registerFont(TTFont("Times", "/System/Library/Fonts/Supplemental/Times New Roman.ttf"))
pdfmetrics.registerFont(TTFont("Times-I", "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"))
pdfmetrics.registerFont(TTFont("Times-B", "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"))
pdfmetrics.registerFont(TTFont("Times-BI", "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf"))
pdfmetrics.registerFont(TTFont("Georgia", "/System/Library/Fonts/Supplemental/Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-I", "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"))

INK = HexColor("#1c1814")
MUTED = HexColor("#5c5348")
RULE = HexColor("#8a6a32")
CREAM = HexColor("#f7f1e6")
OXBLOOD = HexColor("#6e2c24")

PAGE_W, PAGE_H = 6 * inch, 9 * inch


def styles_for(book):
    accent = HexColor(book["accent"])
    return {
        "kicker": ParagraphStyle(
            "kicker",
            fontName="Georgia",
            fontSize=8.5,
            leading=12,
            textColor=accent,
            alignment=TA_CENTER,
        ),
        "title": ParagraphStyle(
            "title",
            fontName="Caslon",
            fontSize=28,
            leading=32,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Georgia-I",
            fontSize=11,
            leading=16,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "center": ParagraphStyle(
            "center",
            fontName="Times",
            fontSize=10.5,
            leading=16,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "center_i": ParagraphStyle(
            "center_i",
            fontName="Times-I",
            fontSize=10.5,
            leading=16,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Caslon",
            fontSize=16,
            leading=20,
            textColor=INK,
            alignment=TA_CENTER,
            spaceBefore=8,
            spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Times-B",
            fontSize=11.5,
            leading=16,
            textColor=accent,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=12,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Times",
            fontSize=10.5,
            leading=15.6,
            textColor=INK,
            alignment=TA_JUSTIFY,
            firstLineIndent=16,
            spaceAfter=8,
        ),
        "body_first": ParagraphStyle(
            "body_first",
            fontName="Times",
            fontSize=10.5,
            leading=15.6,
            textColor=INK,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            spaceAfter=8,
        ),
        "epigraph": ParagraphStyle(
            "epigraph",
            fontName="Times-I",
            fontSize=10,
            leading=14.5,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "maxim": ParagraphStyle(
            "maxim",
            fontName="Times-BI",
            fontSize=10.5,
            leading=15,
            textColor=OXBLOOD,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "exercise": ParagraphStyle(
            "exercise",
            fontName="Times-I",
            fontSize=10,
            leading=14.5,
            textColor=MUTED,
            alignment=TA_JUSTIFY,
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "toc": ParagraphStyle(
            "toc",
            fontName="Times",
            fontSize=11,
            leading=20,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Georgia",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "running": ParagraphStyle(
            "running",
            fontName="Georgia",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def header_footer(book):
    running = book["running"]

    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        if doc.page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.4)
            canvas.line(0.75 * inch, PAGE_H - 0.55 * inch, PAGE_W - 0.75 * inch, PAGE_H - 0.55 * inch)
            canvas.setFillColor(MUTED)
            canvas.setFont("Georgia", 8)
            canvas.drawCentredString(PAGE_W / 2, PAGE_H - 0.45 * inch, running)
            canvas.line(0.75 * inch, 0.55 * inch, PAGE_W - 0.75 * inch, 0.55 * inch)
            canvas.drawString(0.75 * inch, 0.38 * inch, running)
            canvas.drawRightString(PAGE_W - 0.75 * inch, 0.38 * inch, str(doc.page))
        canvas.restoreState()

    return draw


def p(text, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


def build_book(book):
    S = styles_for(book)
    path = EBOOKS / f"{book['slug']}.pdf"
    EBOOKS.mkdir(exist_ok=True)

    doc = BaseDocTemplate(
        str(path),
        pagesize=(PAGE_W, PAGE_H),
        title=book["title"],
        author="The Wump Institute",
        subject=book["subtitle"],
    )
    frame = Frame(
        0.8 * inch,
        0.75 * inch,
        PAGE_W - 1.6 * inch,
        PAGE_H - 1.5 * inch,
        id="normal",
        showBoundary=0,
    )
    doc.addPageTemplates([PageTemplate(id="book", frames=frame, onPage=header_footer(book))])

    story = []
    story.append(Spacer(1, 1.15 * inch))
    story.append(p("THE WUMP INSTITUTE", S["kicker"]))
    story.append(Spacer(1, 0.18 * inch))
    story.append(p(book["title"], S["title"]))
    story.append(p(book["subtitle"], S["subtitle"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(p("·", S["center"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(p(book["volume"], S["center"]))
    story.append(p("womptolive.biz", S["center_i"]))
    story.append(PageBreak())

    story.append(Spacer(1, 0.6 * inch))
    story.append(p("A NOTE ON METHOD", S["h2"]))
    for para in book["disclaimer"]:
        story.append(p(para, S["body_first"] if para == book["disclaimer"][0] else S["body"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(p("Published by the Institute for Applied Whumping<br/>First edition, 2026", S["center_i"]))
    story.append(PageBreak())

    story.append(Spacer(1, 0.35 * inch))
    story.append(p("Contents", S["h1"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(p("Preface", S["toc"]))
    for i, ch in enumerate(book["chapters"], 1):
        story.append(p(f"{i}.  {ch['title']}", S["toc"]))
    if book.get("glossary"):
        story.append(p("Appendix: A Short Glossary", S["toc"]))
    if book.get("notes"):
        story.append(p("Notes for Students of the Institute", S["toc"]))
    story.append(p("Closing Theorem", S["toc"]))
    story.append(PageBreak())

    story.append(Spacer(1, 0.2 * inch))
    story.append(p("Preface", S["h1"]))
    story.append(p(book["preface_epigraph"], S["epigraph"]))
    story.append(p(f"— {book['preface_attr']}", S["center_i"]))
    story.append(Spacer(1, 0.22 * inch))
    for i, para in enumerate(book["preface"]):
        story.append(p(para, S["body_first"] if i == 0 else S["body"]))
    story.append(PageBreak())

    for n, ch in enumerate(book["chapters"], 1):
        blocks = [p(f"Chapter {n}", S["h2"]), p(ch["title"], S["h1"])]
        if ch.get("epigraph"):
            blocks += [p(ch["epigraph"], S["epigraph"]), Spacer(1, 0.12 * inch)]
        for i, para in enumerate(ch["body"]):
            blocks.append(p(para, S["body_first"] if i == 0 else S["body"]))
        blocks.append(p(f"Wump Maxim. {ch['maxim']}", S["maxim"]))
        blocks.append(p(f"Field exercise. {ch['exercise']}", S["exercise"]))
        story.append(KeepTogether(blocks[:3]))
        story.extend(blocks[3:])
        story.append(PageBreak())

    if book.get("glossary"):
        story.append(Spacer(1, 0.15 * inch))
        story.append(p("Appendix: A Short Glossary", S["h1"]))
        story.append(p("Definitions are operational, not eternal. Use them until they stop helping.", S["center_i"]))
        story.append(Spacer(1, 0.16 * inch))
        for term, definition in book["glossary"]:
            story.append(p(f"<b>{term}.</b> {definition}", S["body_first"]))
        story.append(PageBreak())

    if book.get("notes"):
        story.append(p("Notes for Students of the Institute", S["h1"]))
        for i, para in enumerate(book["notes"]):
            story.append(p(para, S["body_first"] if i == 0 else S["body"]))
        story.append(PageBreak())

    story.append(Spacer(1, 0.25 * inch))
    story.append(p("Closing Theorem", S["h1"]))
    for i, para in enumerate(book["closing"]):
        story.append(p(para, S["body_first"] if i == 0 else S["body"]))
    story.append(Spacer(1, 0.28 * inch))
    story.append(p(book["final_line"], S["maxim"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(p("There is no final wump. There is only the practice of returning.", S["center_i"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(p("END OF VOLUME", S["kicker"]))

    doc.build(story)
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main():
    for book in BOOKS:
        build_book(book)


if __name__ == "__main__":
    main()
