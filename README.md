# 📝 TypeNotes

Type your class notes, turn them into a clean PDF, download it and share it.
Built for anyone whose handwriting makes sharing notes hard.

## Features
- Simple formatting: headings, bullets, numbered lists, bold, italic, highlight, important boxes
- Live PDF preview and one-click download
- 4 themes: Clean Blue, Warm Orange, Forest Green, Ruled Paper
- Notebook: save notes by subject, reopen them, search all notes
- Share as PDF (attach in WhatsApp/Messenger) or send the text via WhatsApp/email
- Optional AI tidy-up (spelling and grammar) using the Anthropic API //Dont Have any API KEY Right now so you cant use this feature.

## Run it
```
git clone https://github.com/mubtashimrafid/TypeNotes.git
cd TypeNotes
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501

## Notes syntax
```
# Heading            ## Sub heading
- bullet             1. numbered
> important box      ---  (divider line)
**bold**   *italic*   ==highlight==
```

## Optional: AI tidy-up
This button needs your own Anthropic API key (paid, from console.anthropic.com).
The rest of the app works without it.

Windows:  `set ANTHROPIC_API_KEY=your_key`
Mac/Linux: `export ANTHROPIC_API_KEY=your_key`

## Known limits
- Latin letters and common symbols only; Bangla/Arabic need extra font and text-shaping support (contributions welcome!)
- Saved notes are stored locally in the `notes/` folder

## Ideas for contributors
- Bangla and other language support
- Export to DOCX
- Online share links
- More themes

## Contributing
Pull requests are welcome. Fork the repo, make your change, and open a PR.

## License
MIT. See [LICENSE].
