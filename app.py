"""TypeNotes - type your notes, export a neat PDF, share it.

Run:  streamlit run app.py
"""
import json
import os
import re
import urllib.parse
from datetime import date
from pathlib import Path

import streamlit as st

from pdf_maker import THEMES, make_pdf

NOTES_DIR = Path(__file__).parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="TypeNotes", page_icon="📝", layout="wide")

SAMPLE = """# Photosynthesis
Plants make their own food using **sunlight**, water and carbon dioxide.

## Key points
- Happens in the *chloroplasts*
- Chlorophyll absorbs light, mostly red and blue
- Produces glucose and ==oxygen==

> Exam tip: remember the equation 6CO2 + 6H2O -> C6H12O6 + 6O2

---

## Steps
1. Light energy is absorbed
2. Water is split
3. Glucose is built
"""


# ------------------------------------------------------------ storage helpers
def slug(text):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text.strip()).strip("_") or "untitled"


def save_note(subject, title, author, body, theme):
    folder = NOTES_DIR / slug(subject or "General")
    folder.mkdir(exist_ok=True)
    data = dict(subject=subject, title=title, author=author,
                body=body, theme=theme)
    (folder / f"{slug(title)}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_notes():
    items = []
    for f in sorted(NOTES_DIR.glob("*/*.json")):
        try:
            items.append((f, json.loads(f.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return items


def load_into_editor(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    st.session_state.subject = d.get("subject", "")
    st.session_state.title = d.get("title", "")
    st.session_state.author = d.get("author", "")
    st.session_state.body = d.get("body", "")
    st.session_state.theme = d.get("theme", "Clean Blue")


def ai_cleanup(text):
    """Optional: fix spelling/grammar with Claude. Needs ANTHROPIC_API_KEY."""
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.getenv("TYPENOTES_MODEL", "claude-sonnet-5-5"),
        max_tokens=2000,
        system=("You tidy student notes. Fix spelling and grammar, keep the "
                "meaning, keep the same markdown-style symbols (#, ##, -, "
                "1., >, ---, **bold**, *italic*, ==highlight==). Do not add "
                "new facts. Return only the cleaned notes."),
        messages=[{"role": "user", "content": text}],
    )
    return msg.content[0].text


# ------------------------------------------------------------ session defaults
for k, v in dict(subject="", title="", author="", body="",
                 theme="Clean Blue").items():
    st.session_state.setdefault(k, v)

# ------------------------------------------------------------ sidebar library
with st.sidebar:
    st.header("📚 My Notebook")
    query = st.text_input("🔍 Search notes", placeholder="title, subject or word")
    notes = list_notes()
    if query:
        q = query.lower()
        notes = [(f, d) for f, d in notes
                 if q in d.get("title", "").lower()
                 or q in d.get("subject", "").lower()
                 or q in d.get("body", "").lower()]
    if not notes:
        st.caption("No saved notes yet.")
    current_subject = None
    for f, d in notes:
        subj = d.get("subject") or "General"
        if subj != current_subject:
            st.markdown(f"**{subj}**")
            current_subject = subj
        c1, c2 = st.columns([5, 1])
        c1.button(d.get("title", f.stem), key=f"open_{f}", width="stretch",
                  on_click=load_into_editor, args=(f,))
        if c2.button("🗑", key=f"del_{f}"):
            f.unlink()
            st.rerun()
    st.divider()
    if st.button("➕ New note", width="stretch"):
        for k in ("subject", "title", "body"):
            st.session_state[k] = ""
        st.rerun()

# ------------------------------------------------------------ main page
st.title("📝 TypeNotes")
st.caption("Type your notes, turn them into a neat PDF, and share with your classmates.")

left, right = st.columns([1, 1], gap="large")

with left:
    c1, c2 = st.columns(2)
    c1.text_input("Subject", key="subject", placeholder="e.g. Biology")
    c2.text_input("Note title", key="title", placeholder="e.g. Photosynthesis")
    c3, c4 = st.columns(2)
    c3.text_input("Your name", key="author")
    note_date = c4.date_input("Date", value=date.today())
    st.selectbox("Theme", list(THEMES), key="theme")

    st.text_area("Your notes", key="body", height=380)

    with st.expander("✍️ Formatting cheat sheet"):
        st.markdown(
            "- `# Heading` and `## Sub heading`\n"
            "- `- point` for bullets, `1. point` for numbers\n"
            "- `> text` for an important box, `---` for a line\n"
            "- `**bold**`, `*italic*`, `==highlight==`")

    b1, b2 = st.columns(2)
    if b1.button("💾 Save to notebook", width="stretch"):
        if not st.session_state.title.strip():
            st.warning("Please add a note title first.")
        else:
            save_note(st.session_state.subject, st.session_state.title,
                      st.session_state.author, st.session_state.body,
                      st.session_state.theme)
            st.success("Saved!")
            st.rerun()

    if b2.button("✨ AI tidy-up (optional)", width="stretch",
                 help="Fixes spelling and grammar. Needs ANTHROPIC_API_KEY."):
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.info("Optional feature: set the ANTHROPIC_API_KEY environment "
                    "variable to use it. Everything else works without it.")
        else:
            try:
                with st.spinner("Tidying..."):
                    st.session_state.body = ai_cleanup(st.session_state.body)
                st.rerun()
            except Exception as e:
                st.error(f"AI tidy-up failed: {e}")

with right:
    st.subheader("Preview and share")
    pdf_bytes = make_pdf(
        st.session_state.title, st.session_state.subject,
        st.session_state.author, note_date.strftime("%d %b %Y"),
        st.session_state.body, st.session_state.theme)

    file_name = f"{slug(st.session_state.title or 'notes')}.pdf"
    st.download_button("⬇️ Download PDF", pdf_bytes, file_name=file_name,
                       mime="application/pdf", type="primary",
                       width="stretch")

    # Preview: render PDF pages as images (works in every browser)
    try:
        import pypdfium2 as pdfium
        pdf_doc = pdfium.PdfDocument(pdf_bytes)
        for i in range(len(pdf_doc)):
            img = pdf_doc[i].render(scale=1.6).to_pil()
            st.image(img, caption=f"Page {i + 1}", width="stretch")
    except Exception:
        st.info("Preview unavailable. You can still download the PDF.")

    st.markdown("**Share it**")
    st.caption("Download the PDF, then attach it in your chat app. "
               "Or send the plain text straight away:")
    msg = f"{st.session_state.title}\n\n{st.session_state.body}"
    wa = "https://wa.me/?text=" + urllib.parse.quote(msg[:3000])
    mail = ("mailto:?subject=" + urllib.parse.quote(st.session_state.title or "Notes")
            + "&body=" + urllib.parse.quote(msg[:1500]))
    s1, s2 = st.columns(2)
    s1.link_button("💬 WhatsApp (text)", wa, width="stretch")
    s2.link_button("✉️ Email (text)", mail, width="stretch")
