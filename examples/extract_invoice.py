import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from azure_docintel_extract import DocumentExtractor

# Load environment variables
load_dotenv()

console = Console()

def main():
    # Get Azure credentials from environment variables
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not key:
        console.print("[red]Please set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables[/red]")
        return
    
    # Initialize extractor
    extractor = DocumentExtractor(endpoint=endpoint, key=key)
    
    # Example document path (replace with your document)
    document_path = Path("samples/sample_invoice.pdf")
    
    if not document_path.exists():
        console.print(f"[red]Document not found: {document_path}[/red]")
        return
    
    # Extract invoice data
    invoice = extractor.extract_invoice(document_path)
    
    if invoice:
        console.print("[green]Successfully extracted invoice data:[/green]")
        console.print(f"Invoice Number: {invoice.invoice_number}")
        console.print(f"Date: {invoice.date}")
        console.print(f"Vendor: {invoice.vendor_name}")
        console.print(f"Total Amount: ${invoice.total_amount:,.2f}")
        
        if invoice.billing_address:
            console.print("\nBilling Address:")
            console.print(f"  {invoice.billing_address.street}")
            console.print(f"  {invoice.billing_address.city}, {invoice.billing_address.state} {invoice.billing_address.postal_code}")
        
        if invoice.line_items:
            console.print("\nLine Items:")
            for item in invoice.line_items:
                console.print(f"- {item['description']}: {item['quantity']} x ${item['unit_price']:,.2f} = ${item['amount']:,.2f}")

if __name__ == "__main__":
    main()
