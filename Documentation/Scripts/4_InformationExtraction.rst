Information Extraction 
======

In our project, we will proceed for information Extraction by using Mistral, PaddleOCR, and PyPDF2

- **Mistral** for advanced natural language processing (NLP).
- **PaddleOCR** for Optical Character Recognition (OCR).
- **PyPDF2** for parsing and extracting text from standard PDFs.


Pipeline Workflow
----------------


**1. File Processing**
The system detects the file type and applies the appropriate method for text extraction:
- **PDFs**: Processed using **PyPDF2** for text-based PDFs or **PaddleOCR** for scanned ones.
- **Images**: Directly processed using **PaddleOCR**.

**2. Text Extraction**

Here is a quick tutorial on how to proceed with the text extraction:


[**Open in Google Colab**](https://colab.research.google.com/drive/1RNa_m7HNg_6SUnhLvpMKKC9ERKk2tPTU?authuser=0#scrollTo=kc03xzO2DN1e)




