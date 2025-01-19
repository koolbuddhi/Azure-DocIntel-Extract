from typing import Optional, List
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City name")
    state: str = Field(description="State or province")
    postal_code: str = Field(description="Postal or ZIP code")
    country: Optional[str] = Field(default=None, description="Country name")

class Invoice(BaseModel):
    invoice_number: str = Field(description="Invoice number or identifier")
    date: str = Field(description="Invoice date")
    due_date: Optional[str] = Field(default=None, description="Payment due date")
    total_amount: float = Field(description="Total invoice amount")
    vendor_name: str = Field(description="Name of the vendor/company")
    billing_address: Optional[Address] = Field(default=None, description="Billing address")
    line_items: List[dict] = Field(default_factory=list, description="List of invoice line items")
