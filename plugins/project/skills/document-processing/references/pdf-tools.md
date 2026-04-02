# PDF Extraction Tools Comparison

## Tool Overview

| Tool | Type | Strengths | Weaknesses |
|------|------|-----------|------------|
| **pymupdf** | Python lib | Fast, preserves layout, markdown output | Large dependency |
| **pdftotext** | CLI (poppler) | Simple, reliable, fast | No layout preservation |
| **pdfplumber** | Python lib | Excellent table extraction | Slower on large files |
| **pypdf** | Python lib | Pure Python, no dependencies | Basic text extraction |
| **tesseract** | CLI + lib | OCR for scanned docs | Requires image conversion |
| **Mistral OCR** | API | Best accuracy for complex layouts | Requires API key, costs money |
| **pandoc** | CLI | Multi-format conversion | Not great for complex PDFs |

## When to Use What

### Native PDFs (with text layer)

**First choice: pymupdf**
```python
import pymupdf
doc = pymupdf.open("input.pdf")
for page in doc:
    # Markdown output preserves headers, lists, formatting
    text = page.get_text("markdown")
```

**Simple extraction: pdftotext**
```bash
pdftotext input.pdf output.txt
# Or with layout preservation
pdftotext -layout input.pdf output.txt
```

**Table-heavy documents: pdfplumber**
```python
import pdfplumber
with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        text = page.extract_text()
```

### Scanned PDFs (image-only)

**Best accuracy: Mistral OCR API**
- Handles complex layouts, tables, mixed content
- Costs per page but highest quality

**Offline: tesseract**
```bash
# Convert PDF to images first
pdftoppm -png -r 300 input.pdf page
# OCR each page
for f in page-*.png; do tesseract "$f" "${f%.png}"; done
```

### Document Conversion

**General conversion: pandoc**
```bash
# DOCX to Markdown
pandoc input.docx -t markdown -o output.md

# HTML to Markdown
pandoc input.html -t markdown -o output.md

# LaTeX to Markdown
pandoc input.tex -t markdown -o output.md
```

## Installation

```bash
# Python libraries
uv add pymupdf pdfplumber pypdf

# CLI tools (macOS)
brew install poppler  # provides pdftotext, pdftoppm
brew install tesseract
brew install pandoc

# CLI tools (Ubuntu)
sudo apt-get install poppler-utils tesseract-ocr pandoc
```
