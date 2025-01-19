import os
from typing import Optional
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from rich.console import Console
from .models import Invoice, Address

console = Console()

class DocumentExtractor:
    def __init__(self, endpoint: str, key: str):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
    
    def extract_invoice(self, document_path: str | Path) -> Optional[Invoice]:
        """
        Extract invoice information from a document using Azure Document Intelligence.
        
        Args:
            document_path: Path to the document file
        
        Returns:
            Invoice: Extracted invoice data in structured format
        """
        try:
            with open(document_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-invoice", document=f
                )
            result = poller.result()

            if len(result.documents) == 0:
                console.print("[red]No invoice data found in document[/red]")
                return None

            doc = result.documents[0]
            
            # Extract address if available
            billing_address = None
            if hasattr(doc, "vendor_address"):
                addr = doc.vendor_address
                billing_address = Address(
                    street=addr.street_address or "",
                    city=addr.city or "",
                    state=addr.state or "",
                    postal_code=addr.postal_code or "",
                    country=addr.country or None
                )

            # Create invoice object
            invoice = Invoice(
                invoice_number=doc.invoice_number or "",
                date=doc.invoice_date or "",
                due_date=doc.due_date,
                total_amount=float(doc.total or 0.0),
                vendor_name=doc.vendor_name.value if doc.vendor_name else "",
                billing_address=billing_address,
                line_items=[
                    {
                        "description": item.description.value if item.description else "",
                        "quantity": item.quantity or 0,
                        "unit_price": float(item.unit_price or 0),
                        "amount": float(item.amount or 0)
                    }
                    for item in (doc.items or [])
                ]
            )
            
            return invoice
            
        except Exception as e:
            console.print(f"[red]Error extracting invoice data: {str(e)}[/red]")
            return None
