# OCR Configuration Reference

## Tesseract Configuration

### Page Segmentation Modes (--psm)

| Mode | Description | Best For |
|------|-------------|----------|
| 0 | Orientation and script detection only | Preprocessing |
| 1 | Auto with OSD | General documents |
| 3 | Fully automatic (default) | Most documents |
| 4 | Single column of variable-size text | Articles, papers |
| 6 | Single uniform block of text | Paragraphs |
| 7 | Single text line | Captions, headers |
| 8 | Single word | Labels |
| 11 | Sparse text | Forms, mixed layouts |
| 12 | Sparse text with OSD | Complex layouts |

### OCR Engine Modes (--oem)

| Mode | Description |
|------|-------------|
| 0 | Legacy engine only |
| 1 | Neural nets LSTM engine only |
| 2 | Legacy + LSTM |
| 3 | Default (based on what's available) |

### Language Packs

```bash
# Install additional languages
# macOS
brew install tesseract-lang

# Ubuntu
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-fra  # French

# Use multiple languages
tesseract input.png output -l eng+deu+fra
```

## Image Preprocessing

Improve OCR accuracy with preprocessing:

```python
from PIL import Image, ImageFilter, ImageEnhance

def preprocess_for_ocr(image_path: str) -> Image:
    img = Image.open(image_path)

    # Convert to grayscale
    img = img.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    # Binarize (threshold)
    img = img.point(lambda x: 0 if x < 128 else 255, '1')

    return img
```

### Common preprocessing steps:
1. **Deskew**: Rotate to align text horizontally
2. **Denoise**: Remove speckles and artifacts
3. **Binarize**: Convert to black and white
4. **Scale**: Upscale small text (target 300 DPI)
5. **Border removal**: Remove dark borders from scans

## Mistral OCR API

### Configuration

```python
# Model options
MODELS = {
    "fast": "mistral-ocr-latest",      # Fastest, good for clean documents
}

# Request configuration
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB limit
SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "tiff", "bmp", "webp"]
```

### Tips for better results:
- Use PNG over JPEG for text documents (no compression artifacts)
- Keep images at 300 DPI minimum
- Split large pages into sections for complex layouts
- Use specific prompts for structured data ("Extract the table..." vs generic "Extract text")

## PDF to Image Conversion

```bash
# Using pdftoppm (poppler-utils)
pdftoppm -png -r 300 input.pdf output  # 300 DPI PNG files

# Using ImageMagick (if poppler not available)
convert -density 300 input.pdf output-%04d.png

# Using pymupdf (Python)
import pymupdf
doc = pymupdf.open("input.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    pix.save(f"page-{i:04d}.png")
```
