# Azure Document Intelligence Extractor

A Python library for extracting structured data from documents using Azure Document Intelligence (formerly Form Recognizer) service.

## Features

- Extract invoice data into Pydantic models
- Support for invoice fields like invoice number, dates, amounts, and line items
- Address extraction and validation
- Rich console output for better visibility

## Installation

1. Create and activate a Python virtual environment (Python 3.12+ required):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
uv pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your Azure Document Intelligence credentials:
```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here
```

## Usage

Check the `examples` directory for sample usage. Here's a basic example:

```python
from azure_docintel_extract import DocumentExtractor

extractor = DocumentExtractor(endpoint="your-endpoint", key="your-key")
invoice = extractor.extract_invoice("path/to/invoice.pdf")

print(f"Invoice Number: {invoice.invoice_number}")
print(f"Total Amount: ${invoice.total_amount:,.2f}")
```

## Example

Run the sample invoice extraction script:
```bash
python examples/extract_invoice.py
```

## License

MIT