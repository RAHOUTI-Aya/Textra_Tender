Information Extraction using Mistral, PaddleOCR, and PyPDF2
======

In our project, we will proceed for information Extraction by using Mistral, PaddleOCR, and PyPDF2

- **Mistral** for advanced natural language processing (NLP).
- **PaddleOCR** for Optical Character Recognition (OCR).
- **PyPDF2** for parsing and extracting text from standard PDFs.


Pipeline Workflow
----------------


### 1. File Processing
The system detects the file type and applies the appropriate method for text extraction:
- **PDFs**: Processed using **PyPDF2** for text-based PDFs or **PaddleOCR** for scanned ones.
- **Images**: Directly processed using **PaddleOCR**.

### 2. Text Extraction

#### Using PyPDF2 for Standard PDFs
```python
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()
    return extracted_text
