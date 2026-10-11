# 📝 TypeNotes

Type your class notes **page by page**, turn them into a clean PDF, then download and share it.
Made for anyone whose handwriting makes sharing notes hard.

**🌐 Try it online: https://typenotes.streamlit.app**

> 🚧 **Status: under development.**
> This is a fun, work-in-progress AI-assisted project, made to give one of my ideas a shape.
> Things may change, break, or be improved at any time. Feedback and ideas are welcome!

---

## ✨ Features
- Simple formatting: headings, bullets, numbered lists, bold, italic, highlight, important boxes
- **Page-by-page notebook:** leave a page unfinished, write other pages, and come back to finish it later
- Live preview of the page you are writing, and one-click PDF download (all pages)
- 4 themes: Clean Blue, Warm Orange, Forest Green, Ruled Paper
- Notebook: save notes by subject, reopen them, search all notes
- Share the PDF (attach it in WhatsApp/Messenger) or send the text by WhatsApp/email
- Optional AI tidy-up for spelling and grammar (needs your own API key, see below)

---

## 🚀 How to use it online (PC and phone)
No installation needed. It works in any modern browser on a computer or phone.

1. Open **https://typenotes.streamlit.app**
2. If you see *"This app has gone to sleep"*, click **Yes, get this app back up!** and wait under a minute.
3. Fill in the **Subject**, **Note title**, **Your name** and pick a **Theme**.
4. Type your notes in the box. Tap or click **outside** the box (or press `Ctrl + Enter` on a computer) to update the preview.
5. Need another page? Click **➕ Add page**. Use **◀ ▶** or the dropdown to move between pages and finish any page later.
6. Click **⬇️ Download PDF**, then send the file to your friends.

### On a phone
- Open the link in Chrome or Safari.
- Tap the browser menu and choose **Add to Home screen** to get an app-style icon.
- After downloading, find the PDF in your **Downloads** or **Files** app and attach it in WhatsApp, Messenger or email.

### Good to know about the online version
- Saved notes on the online app are **not private or permanent**. Anyone can open the same link, and the server can reset. **Always download your PDF.**
- Don't type private information into the online app.

---

## 💻 How to run it on your own computer
Your saved notebook stays on your computer and nothing goes to a shared server.

**1. Install Python** (3.9 or newer) from python.org. On Windows, tick **"Add Python to PATH"**.

**2. Get the code.** Either download it with **Code → Download ZIP** on this page and unzip it, or use Git:
```
git clone https://github.com/mubtashimrafid/TypeNotes.git
```

**3. Open a terminal in the project folder.**
On Windows: open the folder, click the address bar, type `cmd` and press Enter.

**4. Install the libraries** (one time only):
```
pip install -r requirements.txt
```

**5. Start the app:**
```
streamlit run app.py
```
Your browser opens at http://localhost:8501. Keep the terminal window open while you use it, and press `Ctrl + C` to stop.

### Use it on your phone from your own computer (same Wi-Fi)
Run `streamlit run app.py`. The terminal shows a **Network URL** such as `http://192.168.x.x:8501`. Open that address in your phone's browser while both devices are on the same Wi-Fi.

---

## ✍️ Notes syntax
```
# Heading            ## Sub heading
- bullet             1. numbered
> important box      ---  (divider line)
**bold**   *italic*   ==highlight==
```
A page holds about 37 lines. If a page has more, it continues onto an extra sheet in the PDF.

---

## 🤖 Optional: AI tidy-up
The **AI tidy-up** button fixes spelling and grammar on the page you are on. It needs your own Anthropic API key (paid, from console.anthropic.com).
It is **not enabled on the online version**, and everything else works without it.

Windows: `set ANTHROPIC_API_KEY=your_key`
Mac/Linux: `export ANTHROPIC_API_KEY=your_key`

---

## ⚠️ Known limits
- Latin letters and common symbols only. Bangla and Arabic need extra font and text-shaping support (contributions welcome!)
- The free online app goes to sleep when unused and may need one click to wake up
- Under development: expect rough edges

## 💡 Ideas for the future
- Bangla and other language support
- Export to DOCX
- Permanent online notebooks and share links
- More themes
- A football match predictor in the same app

## 🤝 Contributing
Pull requests and ideas are welcome. Fork the repo, make your change, and open a pull request.

## 📄 License
MIT. See [LICENSE](LICENSE).
