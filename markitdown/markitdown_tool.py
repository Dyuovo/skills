#!/usr/bin/env python3
"""
markitdown_tool — Python wrapper for Microsoft MarkItDown.
Converts PDF, DOCX, PPTX, XLSX, HTML, images, audio, EPUB, ZIP
and more into clean Markdown for LLM consumption.

Usage:
    python3 markitdown_tool.py input.pdf -o output.md
    python3 markitdown_tool.py input.docx --stdout
    python3 markitdown_tool.py --help
"""

import argparse
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_VENV_BASE = os.path.join(_SCRIPT_DIR, "..", "..", "config", "venvs", "markitdown")
_VENV_SITE = os.path.join(_VENV_BASE, "lib")
_REPO_SRC = os.path.join(_SCRIPT_DIR, "..", "..", "config", "markitdown_repo", "packages", "markitdown", "src")

_CANDIDATE_PATHS = [
    _REPO_SRC,
    os.path.join(_VENV_SITE, "python3.12", "site-packages"),
    os.path.join(_VENV_SITE, "python3.11", "site-packages"),
    os.path.join(_VENV_SITE, "python3.10", "site-packages"),
]

for _p in _CANDIDATE_PATHS:
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

# Prepend venv bin to PATH so pip-installed scripts resolve
_venv_bin = os.path.join(_VENV_BASE, "bin")
if os.path.isdir(_venv_bin) and _venv_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _venv_bin + os.pathsep + os.environ.get("PATH", "")

try:
    from markitdown import MarkItDown
    from markitdown._exceptions import FileConversionException, UnsupportedFormatException
    HAS_MARKITDOWN = True
except ImportError:
    HAS_MARKITDOWN = False


_FALLBACK_MIMES = {
    ".txt":  "text/plain",
    ".md":   "text/markdown",
    ".csv":  "text/csv",
    ".json": "application/json",
    ".jsonl":"application/jsonl",
    ".xml":  "text/xml",
    ".html": "text/html",
    ".htm":  "text/html",
    ".log":  "text/plain",
    ".yaml": "text/yaml",
    ".yml":  "text/yaml",
    ".toml": "text/plain",
    ".ini":  "text/plain",
    ".cfg":  "text/plain",
    ".sh":   "text/plain",
    ".py":   "text/plain",
    ".js":   "text/plain",
    ".ts":   "text/plain",
    ".css":  "text/css",
}


def _guess_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return _FALLBACK_MIMES.get(ext, "text/plain")


def convert_file(input_path: str, output_path: str | None = None) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if HAS_MARKITDOWN:
        md = MarkItDown()
        result = md.convert(input_path)
        text = result.text_content
    else:
        mime = _guess_mime(input_path)
        with open(input_path, "rb") as fh:
            raw = fh.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="replace")
        text = text.replace("\r\n", "\n")

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Converted → {output_path}")

    return text


def convert_stdin(output_path: str | None = None) -> str:
    data = sys.stdin.buffer.read()

    if HAS_MARKITDOWN:
        import io
        from markitdown import StreamInfo
        md = MarkItDown()
        stream = StreamInfo(io.BytesIO(data), "application/octet-stream", ".bin")
        result = md.convert_stream(stream)
        text = result.text_content
    else:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1", errors="replace")
        text = text.replace("\r\n", "\n")

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Converted → {output_path}")

    return text


def main():
    parser = argparse.ArgumentParser(
        description="Convert files to Markdown using Microsoft MarkItDown.",
        prog="markitdown_tool",
    )
    parser.add_argument("input", nargs="?", help="Input file path (reads stdin if omitted)")
    parser.add_argument("-o", "--output", help="Output .md file path")
    parser.add_argument("--stdout", action="store_true", help="Force stdout output even when -o is given")

    args = parser.parse_args()

    try:
        if args.input:
            text = convert_file(args.input, args.output)
        else:
            text = convert_stdin(args.output)

        if args.stdout or not args.output:
            sys.stdout.write(text)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (FileConversionException, UnsupportedFormatException) as e:
        print(f"Conversion error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
