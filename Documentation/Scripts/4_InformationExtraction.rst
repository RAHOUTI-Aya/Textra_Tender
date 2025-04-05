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


<div style="border:1px solid #E5E5E5; border-radius:8px; padding:15px; width:fit-content; background-color:#F9F9F9;">
    <p style="font-weight:bold; margin:0; color:#0F9D58;">Hint</p>
    <p style="margin-top:5px;">Before jumping into the next Colab, ensure that you close the previous one and reconnect to the Colab GPU to free memory space, avoiding OutOfMemory errors.</p>
    <a href="https://colab.research.google.com/drive/1RNa_m7HNg_6SUnhLvpMKKC9ERKk2tPTU?authuser=0#scrollTo=kc03xzO2DN1e" target="_blank" style="text-decoration:none;">
        <button style="padding:10px 15px; background-color:#4285F4; color:white; border:none; border-radius:5px; display:flex; align-items:center; cursor:pointer;">
            <img src="https://colab.research.google.com/img/colab_favicon_256px.png" style="width:20px; height:20px; margin-right:8px;">
            Open in Colab
        </button>
    </a>
</div>




