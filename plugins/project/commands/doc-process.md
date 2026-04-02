---
description: Process documents with OCR, text extraction, and conversion
argument-hint: <file-or-directory> [--format markdown|json|text]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Document Processing

Extract, convert, and structure content from documents. Load the `project:document-processing` skill for reference.

## Process

### 1. Identify Input
!echo "Input: $ARGUMENTS"

Parse arguments:
- First argument: file path or directory
- `--format`: output format (markdown, json, text). Default: markdown

### 2. Detect Document Type
For each input file, determine processing approach:
- Check if PDF has native text layer
- Check if input is image (PNG, JPG, TIFF)
- Check if input is a directory (batch mode)

### 3. Process
Based on document type, use appropriate extraction method:
- Native PDF: `pymupdf` or `pdftotext`
- Scanned PDF/Images: Mistral OCR API or tesseract
- Word documents: `python-docx` or `pandoc`

### 4. Structure Output
Clean up extracted text:
- Fix OCR artifacts
- Reconstruct tables
- Identify headers
- Extract structured data if requested (emails, dates, etc.)

### 5. Save Results
Write output to file(s) in requested format alongside the input.
