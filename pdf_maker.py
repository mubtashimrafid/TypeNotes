"""pdf_maker.py - turns typed notes into a clean, shareable PDF.

Notes syntax (simple, like chat apps):
    # Big heading
    ## Sub heading
    - bullet point        (or * bullet)
    1. numbered point
    > important note (shown in a highlighted box)
    ---                   (horizontal line)
    **bold**  *italic*  ==highlighted==
"""
import io
import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# ---------------------------------------------------------------- themes
THEMES = {
    "Clean Blue": dict(h1="#1F4E79", h2="#2E75B6", accent="#2E75B6",
                       note_bg="#EAF2FB", ruled=False),
    "Warm Orange": dict(h1="#B34700", h2="#E36C0A", accent="#E36C0A",
                        note_bg="#FFF2E5", ruled=False),
    "Forest Green": dict(h1="#1E5631", h2="#2E8B57", accent="#2E8B57",
                         note_bg="#E8F5EC", ruled=False),
    "Ruled Paper": dict(h1="#222222", h2="#444444", accent="#C0392B",
                        note_bg="#FFF9DB", ruled=True),
}

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/Library/Fonts",
    "C:/Windows/Fonts",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
]


def _register_fonts():
    """Use DejaVu Sans (supports many symbols) if found, else Helvetica."""
    for d in _FONT_DIRS:
        reg, bold, ital = (os.path.join(d, n) for n in
                           ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
                            "DejaVuSans-Oblique.ttf"))
        if all(os.path.exists(p) for p in (reg, bold, ital)):
            pdfmetrics.registerFont(TTFont("TN", reg))
            pdfmetrics.registerFont(TTFont("TN-B", bold))
            pdfmetrics.registerFont(TTFont("TN-I", ital))
            pdfmetrics.registerFontFamily("TN", normal="TN", bold="TN-B",
                                          italic="TN-I", boldItalic="TN-B")
            return "TN", "TN-B"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = _register_fonts()


# ---------------------------------------------------------------- helpers
def _inline(text):
    """Escape text, then apply **bold**, *italic*, ==highlight==."""
    t = escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"==(.+?)==", r'<font backColor="#FFF176">\1</font>', t)
    return t


def _styles(theme):
    c = THEMES[theme]
    base = ParagraphStyle("base", fontName=FONT, fontSize=11, leading=17,
                          alignment=TA_LEFT, textColor=colors.HexColor("#222"))
    return {
        "body": base,
        "h1": ParagraphStyle("h1", parent=base, fontName=FONT_BOLD,
                             fontSize=18, leading=23, spaceBefore=12,
                             spaceAfter=6, textColor=colors.HexColor(c["h1"])),
        "h2": ParagraphStyle("h2", parent=base, fontName=FONT_BOLD,
                             fontSize=14, leading=19, spaceBefore=9,
                             spaceAfter=4, textColor=colors.HexColor(c["h2"])),
        "bullet": ParagraphStyle("bullet", parent=base, leftIndent=16,
                                 bulletIndent=4, spaceAfter=2),
        "note": ParagraphStyle("note", parent=base, fontSize=10.5, leading=16),
    }


def _parse(body, theme):
    st, c = _styles(theme), THEMES[theme]
    story = []
    for raw in body.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            story.append(Spacer(1, 6))
        elif s.startswith("## "):
            story.append(Paragraph(_inline(s[3:]), st["h2"]))
        elif s.startswith("# "):
            story.append(Paragraph(_inline(s[2:]), st["h1"]))
        elif re.fullmatch(r"-{3,}", s):
            story.append(HRFlowable(width="100%", thickness=0.7,
                                    color=colors.HexColor(c["accent"]),
                                    spaceBefore=4, spaceAfter=6))
        elif s.startswith(("- ", "* ")):
            story.append(Paragraph(_inline(s[2:]), st["bullet"],
                                   bulletText="\u2022" if FONT == "TN" else "-"))
        elif re.match(r"\d+[.)] ", s):
            num, rest = re.split(r"[.)] ", s, maxsplit=1)
            story.append(Paragraph(_inline(rest), st["bullet"],
                                   bulletText=f"{num}."))
        elif s.startswith("> "):
            box = Table([[Paragraph(_inline(s[2:]), st["note"])]],
                        colWidths=[170 * mm])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(c["note_bg"])),
                ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(c["accent"])),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story += [Spacer(1, 3), box, Spacer(1, 3)]
        else:
            story.append(Paragraph(_inline(s), st["body"]))
    return story


# ---------------------------------------------------------------- main API
def make_pdf(title, subject, author, date_text, body, theme="Clean Blue"):
    """Return PDF bytes for the given notes."""
    c = THEMES[theme]
    buf = io.BytesIO()
    W, H = A4

    def decorate(canvas, doc):
        canvas.saveState()
        if c["ruled"]:  # faint ruled-paper lines + margin line
            canvas.setStrokeColor(colors.HexColor("#CFE0F1"))
            canvas.setLineWidth(0.5)
            y = H - 30 * mm
            while y > 18 * mm:
                canvas.line(0, y, W, y)
                y -= 8 * mm
            canvas.setStrokeColor(colors.HexColor("#F1A9A0"))
            canvas.line(18 * mm, 0, 18 * mm, H)
        canvas.setFont(FONT, 8.5)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(20 * mm, H - 12 * mm,
                          " | ".join(x for x in (subject, title) if x))
        canvas.drawString(20 * mm, 10 * mm, f"Notes by {author}" if author else "")
        canvas.drawRightString(W - 20 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm,
                            rightMargin=20 * mm, topMargin=22 * mm,
                            bottomMargin=20 * mm, title=title or "Notes",
                            author=author or "", subject=subject or "")
    st = _styles(theme)
    title_style = ParagraphStyle("title", parent=st["h1"], fontSize=24,
                                 leading=29, spaceBefore=0, spaceAfter=4)
    meta = "   \u00b7   ".join(x for x in (subject, author, date_text) if x)
    story = [Paragraph(escape(title or "Untitled Notes"), title_style)]
    if meta:
        story.append(Paragraph(escape(meta), ParagraphStyle(
            "meta", parent=st["body"], fontSize=10,
            textColor=colors.HexColor("#666666"))))
    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=colors.HexColor(c["accent"]),
                            spaceBefore=6, spaceAfter=10))
    story += _parse(body, theme)
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return buf.getvalue()
