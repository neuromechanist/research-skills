---
name: document-processing
description: "Use this skill for \"process documents\", \"extract text from PDF\", \"OCR this document\", \"convert PDF to markdown\", \"extract emails from documents\", \"parse document\", \"document conversion\", \"batch OCR\", \"extract structured data from PDF\", or when the user wants to extract, convert, or process documents."
version: 0.2.0
---

# Document Processing

Extract, convert, and structure content from PDFs, images, and other document formats. Handles OCR, text extraction, markdown conversion, email extraction, and structured data output.

## When to Use

- Converting scanned documents to searchable text
- Extracting text from PDFs (native or scanned)
- Converting documents to markdown for further processing
- Extracting emails, addresses, or other structured data from documents
- Batch processing document collections

## Processing Pipeline

### Step 1: Identify Document Type

Determine the processing approach:

| Input | Method | Tool |
|---|---|---|
| Native PDF (has text layer) | Direct extraction | `pdftotext`, `pymupdf` |
| Scanned PDF (images only) | OCR | Mistral OCR API, `tesseract` |
| Image files (PNG, JPG, TIFF) | OCR | Mistral OCR API, `tesseract` |
| Word documents (.docx) | Conversion | `python-docx`, `pandoc` |
| HTML | Conversion | `pandoc`, `beautifulsoup4` |

Detection:
```bash
# Check if PDF has text content
pdftotext input.pdf - | head -20
# If output is empty or garbled, it's a scanned PDF -> use OCR
```

### Step 2: Extract Content

#### Native PDF Extraction

```python
import pymupdf  # pip: pymupdf

doc = pymupdf.open("input.pdf")
for page in doc:
    text = page.get_text("markdown")  # or "text", "html"
    print(text)
```

#### OCR with Mistral (for scanned documents)

```python
import base64
import httpx

def ocr_page(image_path: str, api_key: str) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = httpx.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "mistral-ocr-latest",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                    {"type": "text", "text": "Extract all text from this image. Preserve formatting, tables, and structure. Output as markdown."}
                ]
            }]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

#### OCR with Tesseract (offline fallback)

```bash
# Single page
tesseract input.png output -l eng --oem 3 --psm 6

# PDF to text via tesseract
pdftoppm input.pdf page -png
for f in page-*.png; do tesseract "$f" "${f%.png}" -l eng; done
cat page-*.txt > output.txt
```

### Step 3: Structure Output

Convert extracted text to structured formats:

#### Markdown cleanup
- Fix OCR artifacts (broken words, spurious line breaks)
- Reconstruct tables from aligned text
- Identify headers from font size/weight changes
- Preserve list formatting

#### Structured data extraction

```python
# Extract emails
import re
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', text)

# Extract dates
dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)

# Extract phone numbers
phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
```

### Step 4: Output

Save results in the requested format:
- Markdown (`.md`) - default for text content
- JSON - for structured data extraction
- Plain text (`.txt`) - for simple text extraction

## Batch Processing

For document collections:

```bash
# Process all PDFs in a directory
for pdf in /path/to/docs/*.pdf; do
  name=$(basename "$pdf" .pdf)
  pdftotext "$pdf" "/path/to/output/${name}.txt"
done
```

For large collections, track progress:
1. Create a manifest of input files
2. Process each file, recording success/failure
3. Report summary (processed, failed, skipped)

## Quality Checks

After extraction, verify:
- [ ] Text is readable (not garbled encoding)
- [ ] Tables preserved their structure
- [ ] No pages were skipped
- [ ] Special characters rendered correctly
- [ ] Headers and sections identified

## Additional Resources

- Reference: [references/ocr-configuration.md](references/ocr-configuration.md) - Tesseract languages, page segmentation modes, preprocessing
- Reference: [references/pdf-tools.md](references/pdf-tools.md) - Comparison of PDF extraction libraries and their tradeoffs
