"""TypeNotes - type your notes page by page, export a neat PDF, share it.

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


# ------------------------------------------------------------ storage helpers
def slug(text):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text.strip()).strip("_") or "untitled"


def full_text(pages):
    return "\n\n".join(p for p in pages if p.strip())


def save_note(subject, title, author, pages, theme):
    folder = NOTES_DIR / slug(subject or "General")
    folder.mkdir(exist_ok=True)
    data = dict(subject=subject, title=title, author=author, pages=pages,
                body=full_text(pages), theme=theme)
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


# ------------------------------------------------------------ page helpers
def purge_page_widgets():
    """Forget the text boxes so they reload from the saved pages."""
    for k in [k for k in st.session_state if k.startswith("pg_")]:
        del st.session_state[k]


def flush():
    """Copy what is typed in the visible text box into the pages list."""
    i = st.session_state.get("shown", 0)
    key = f"pg_{i}"
    if key in st.session_state and i < len(st.session_state.pages):
        st.session_state.pages[i] = st.session_state[key]


def set_page(i):
    """Jump to page i (0-based) and keep the dropdown in step."""
    st.session_state.cur_page = i
    st.session_state.page_pick = i


def pick_page():
    """Called when the user chooses a page in the dropdown."""
    flush()
    v = st.session_state.get("page_pick")
    if isinstance(v, int) and 0 <= v < len(st.session_state.pages):
        st.session_state.cur_page = v


def go_prev():
    flush()
    set_page(max(int(st.session_state.cur_page) - 1, 0))


def go_next():
    flush()
    last = len(st.session_state.pages) - 1
    set_page(min(int(st.session_state.cur_page) + 1, last))


def add_page():
    flush()
    st.session_state.pages.append("")
    set_page(len(st.session_state.pages) - 1)


def delete_page():
    flush()
    pages = st.session_state.pages
    i = st.session_state.cur_page
    if len(pages) > 1:
        pages.pop(i)
    else:
        pages[0] = ""
    purge_page_widgets()
    set_page(min(i, len(pages) - 1))


def load_into_editor(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    st.session_state.subject = d.get("subject", "")
    st.session_state.title = d.get("title", "")
    st.session_state.author = d.get("author", "")
    st.session_state.theme = d.get("theme", "Clean Blue")
    st.session_state.pages = d.get("pages") or [d.get("body", "")]
    purge_page_widgets()
    set_page(0)


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


def run_ai_cleanup():
    flush()
    i = st.session_state.cur_page
    st.session_state.ai_msg = None
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.session_state.ai_msg = ("info", "Optional feature: set the "
                                   "ANTHROPIC_API_KEY environment variable to "
                                   "use it. Everything else works without it.")
        return
    try:
        cleaned = ai_cleanup(st.session_state.pages[i])
        st.session_state.pages[i] = cleaned
        st.session_state[f"pg_{i}"] = cleaned
    except Exception as e:
        st.session_state.ai_msg = ("error", f"AI tidy-up failed: {e}")


# ------------------------------------------------------------ session defaults
for k, v in dict(subject="", title="", author="", pages=[""], cur_page=0,
                 page_pick=0, shown=0, theme="Clean Blue").items():
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
        for k in ("subject", "title"):
            st.session_state[k] = ""
        st.session_state.pages = [""]
        st.session_state.cur_page = 0
        st.session_state.page_pick = 0
        purge_page_widgets()
        st.rerun()

# ------------------------------------------------------------ main page
st.title("📝 TypeNotes")
st.caption("Type your notes page by page, turn them into a neat PDF, and share with your classmates.")

pages = st.session_state.pages
if not isinstance(st.session_state.cur_page, int):
    st.session_state.cur_page = 0
st.session_state.cur_page = max(0, min(st.session_state.cur_page, len(pages) - 1))
cur = st.session_state.cur_page


def page_status(i):
    n = sum(1 for line in pages[i].splitlines() if line.strip())
    return f"{i + 1}: " + (f"{n} lines" if n else "empty")


left, right = st.columns([1, 1], gap="large")

with left:
    c1, c2 = st.columns(2)
    c1.text_input("Subject", key="subject", placeholder="e.g. Biology")
    c2.text_input("Note title", key="title", placeholder="e.g. Photosynthesis")
    c3, c4 = st.columns(2)
    c3.text_input("Your name", key="author")
    note_date = c4.date_input("Date", value=date.today())
    st.selectbox("Theme", list(THEMES), key="theme")

    # ---- page navigation
    n1, n2, n3 = st.columns([1, 4, 1])
    n1.button("◀", on_click=go_prev, disabled=cur == 0, width="stretch",
              help="Previous page")
    st.session_state.page_pick = cur
    n2.selectbox("Page", list(range(len(pages))),
                 format_func=lambda i: f"Page {i + 1}", key="page_pick",
                 on_change=pick_page, label_visibility="collapsed")
    n3.button("▶", on_click=go_next, disabled=cur >= len(pages) - 1,
              width="stretch", help="Next page")
    st.caption("Pages  ·  " + "  ·  ".join(page_status(i) for i in range(len(pages))))
    a1, a2 = st.columns(2)
    a1.button("➕ Add page", on_click=add_page, width="stretch")
    a2.button("🗑 Delete this page", on_click=delete_page, width="stretch")

    # ---- the notes box for the chosen page
    st.session_state.shown = cur
    if f"pg_{cur}" not in st.session_state:
        st.session_state[f"pg_{cur}"] = pages[cur]
    st.text_area(f"Notes for page {cur + 1}", key=f"pg_{cur}", height=340,
                 on_change=flush)
    st.caption("Each page is its own sheet in the PDF. A page holds about 37 "
               "lines; longer text continues onto an extra sheet. Leave a page "
               "unfinished and come back to it later.")

    with st.expander("✍️ Formatting cheat sheet"):
        st.markdown(
            "- `# Heading` and `## Sub heading`\n"
            "- `- point` for bullets, `1. point` for numbers\n"
            "- `> text` for an important box, `---` for a line\n"
            "- `**bold**`, `*italic*`, `==highlight==`")

    b1, b2 = st.columns(2)
    if b1.button("💾 Save to notebook", width="stretch"):
        flush()
        if not st.session_state.title.strip():
            st.warning("Please add a note title first.")
        else:
            save_note(st.session_state.subject, st.session_state.title,
                      st.session_state.author, st.session_state.pages,
                      st.session_state.theme)
            st.toast("Saved to your notebook!", icon="✅")
            st.rerun()

    b2.button("✨ AI tidy-up (optional)", on_click=run_ai_cleanup,
              width="stretch",
              help="Fixes spelling and grammar on this page. Needs ANTHROPIC_API_KEY.")
    msg = st.session_state.get("ai_msg")
    if msg:
        getattr(st, msg[0])(msg[1])

with right:
    st.subheader("Preview and share")
    pdf_bytes, overflow, spans = make_pdf(
        st.session_state.title, st.session_state.subject,
        st.session_state.author, note_date.strftime("%d %b %Y"),
        pages, st.session_state.theme, return_info=True)

    file_name = f"{slug(st.session_state.title or 'notes')}.pdf"
    st.download_button("⬇️ Download PDF", pdf_bytes, file_name=file_name,
                       mime="application/pdf", type="primary", width="stretch")

    if overflow:
        nums = ", ".join(str(i + 1) for i in overflow)
        st.warning(f"Page {nums} has more text than fits on one page, so it "
                   "continues onto an extra sheet in the PDF.")

    # Preview: show only the page you are working on (as pictures, so it
    # works in every browser). The download still contains all pages.
    try:
        import pypdfium2 as pdfium
        pdf_doc = pdfium.PdfDocument(pdf_bytes)
        first, last = spans[cur] if cur < len(spans) else (0, 0)
        for k, sheet in enumerate(range(first, last + 1)):
            img = pdf_doc[sheet].render(scale=1.6).to_pil()
            extra = f" (continues, sheet {k + 1})" if k else ""
            st.image(img, caption=f"Page {cur + 1} of {len(pages)}{extra}",
                     width="stretch")
        st.caption("This preview shows the page you are writing. "
                   "The PDF you download contains all pages.")
    except Exception:
        st.info("Preview unavailable. You can still download the PDF.")

    st.markdown("**Share it**")
    st.caption("Download the PDF, then attach it in your chat app. "
               "Or send the plain text straight away:")
    text = f"{st.session_state.title}\n\n{full_text(pages)}"
    wa = "https://wa.me/?text=" + urllib.parse.quote(text[:3000])
    mail = ("mailto:?subject=" + urllib.parse.quote(st.session_state.title or "Notes")
            + "&body=" + urllib.parse.quote(text[:1500]))
    s1, s2 = st.columns(2)
    s1.link_button("💬 WhatsApp (text)", wa, width="stretch")
    s2.link_button("✉️ Email (text)", mail, width="stretch")
