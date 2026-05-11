---
name: markitdown
description: Convert PDF, DOCX, PPTX, XLSX, images, audio, HTML, EPUB, ZIP and 20+ file formats into clean Markdown for LLM consumption.
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "requires": { "bins": ["python3"] },
      },
  }
---

# markitdown — Document to Markdown Converter

Microsoft MarkItDown converts local files into structured Markdown. Use it whenever the user gives you a file to read or analyze — especially PDFs, Office docs, images (OCR), audio (transcription), HTML, EPUB, and ZIP archives.

## Supported formats

- PDF (text + OCR), DOCX, PPTX, XLSX/XLS, CSV
- HTML, XML, JSON, EPUB, IPYNB
- Images: JPG/PNG/GIF/WEBP (OCR + EXIF)
- Audio: MP3/WAV/OGG (speech transcription)
- YouTube URLs, ZIP archives
- Outlook MSG, RSS feeds, Wikipedia pages

## Commands

```bash
python3 markitdown_tool.py INPUT_FILE -o OUTPUT.md
```

Quick preview (stdout):

```bash
python3 markitdown_tool.py INPUT_FILE --stdout
```

Pipe mode:

```bash
cat somefile.pdf | python3 markitdown_tool.py
```

## First-time setup (one-time only)

The tool works out of the box for plain-text formats. For full format support (PDF, DOCX, XLSX, etc.):

```bash
bash setup_markitdown.sh
```

Or manually install:

```bash
pip install 'markitdown[all]'
```

## Notes

- Output is optimized for LLM consumption, not human reading
- Large PDFs may be slow; consider extracting specific pages first
- Audio transcription requires `SpeechRecognition` + `pydub` installed
- Without optional dependencies, the tool gracefully falls back to plain-text conversion
