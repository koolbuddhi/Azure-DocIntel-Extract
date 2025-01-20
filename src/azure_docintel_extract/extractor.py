import os
from typing import Optional, List
from pathlib import Path
from datetime import datetime
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
    
    def _get_field_value(self, fields: dict, field_name: str, default: any = None) -> any:
        """Helper method to safely get field value"""
        if field_name in fields and fields[field_name].value is not None:
            return fields[field_name].value
        return default
    
    def _get_currency_value(self, value: any, default: float = 0.0) -> float:
        """Helper method to safely get currency value"""
        if hasattr(value, 'amount'):
            return float(value.amount)
        if isinstance(value, (int, float)):
            return float(value)
        return default
    
    def _get_date_value(self, value: any, default: str = '') -> str:
        """Helper method to safely get date value"""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        if isinstance(value, str):
            return value
        return default
    
    def _extract_line_items(self, fields: dict) -> List[dict]:
        """Helper method to extract line items"""
        items = []
        items_field = self._get_field_value(fields, 'Items')
        
        if not items_field:
            return items
            
        # Handle both array and single item cases
        if not isinstance(items_field, list):
            items_field = [items_field]
            
        for item in items_field:
            items.append({
                "description": self._get_field_value(item.value, 'Description', ''),
                "quantity": float(self._get_field_value(item.value, 'Quantity', 0)),
                "unit_price": self._get_currency_value(self._get_field_value(item.value, 'UnitPrice')),
                "amount": self._get_currency_value(self._get_field_value(item.value, 'Amount'))
            })
        
        return items
    
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
            fields = doc.fields
            
            # Extract address if available
            billing_address = None
            billing_addr_field = self._get_field_value(fields, 'BillingAddress')
            if billing_addr_field:
                billing_address = Address(
                    street=self._get_field_value(billing_addr_field, 'StreetAddress', ''),
                    city=self._get_field_value(billing_addr_field, 'City', ''),
                    state=self._get_field_value(billing_addr_field, 'State', ''),
                    postal_code=self._get_field_value(billing_addr_field, 'PostalCode', ''),
                    country=self._get_field_value(billing_addr_field, 'CountryRegion', '')
                )

            # Get invoice total
            total_amount = self._get_field_value(fields, 'InvoiceTotal', 0.0)
            total_amount = self._get_currency_value(total_amount)

            # Extract line items
            line_items = self._extract_line_items(fields)

            # Get date fields
            invoice_date = self._get_field_value(fields, 'InvoiceDate')
            due_date = self._get_field_value(fields, 'DueDate')

            # Create invoice object
            invoice = Invoice(
                invoice_number=self._get_field_value(fields, 'InvoiceId', ''),
                date=self._get_date_value(invoice_date),
                due_date=self._get_date_value(due_date),
                total_amount=total_amount,
                vendor_name=self._get_field_value(fields, 'VendorName', ''),
                billing_address=billing_address,
                line_items=line_items
            )
            
            return invoice
            
        except Exception as e:
            console.print(f"[red]Error extracting invoice data: {str(e)}[/red]")
            return None
