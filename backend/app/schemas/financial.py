"""
Financial Schemas

Pydantic schemas for financial operations API requests and responses.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from uuid import UUID


# Payment Method Schemas
class PaymentMethodCreate(BaseModel):
    """Schema for creating a payment method."""
    type: str = Field(..., max_length=50)  # Changed from enum to string
    provider: str = Field(..., max_length=50)  # Made required
    provider_payment_method_id: str = Field(..., max_length=255)  # Made required
    last_four_digits: Optional[str] = Field(None, max_length=4)
    expiry_month: Optional[int] = Field(None, ge=1, le=12)
    expiry_year: Optional[int] = Field(None, ge=2024)
    cardholder_name: Optional[str] = Field(None, max_length=100)  # Added
    is_default: bool = False


class PaymentMethodUpdate(BaseModel):
    """Schema for updating a payment method."""
    is_default: Optional[bool] = None


class PaymentMethodResponse(BaseModel):
    """Schema for payment method response."""
    id: str
    user_id: str
    type: str  # Changed from enum to string
    provider: str
    provider_payment_method_id: str
    last_four_digits: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    cardholder_name: Optional[str] = None  # Added
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Billing Address Schemas
class BillingAddressCreate(BaseModel):
    """Schema for creating a billing address."""
    street_address: str = Field(..., max_length=255)  # Changed from address_line_1
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)  # Changed from 2 to 100
    is_default: bool = False


class BillingAddressUpdate(BaseModel):
    """Schema for updating a billing address."""
    street_address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None


class BillingAddressResponse(BaseModel):
    """Schema for billing address response."""
    id: UUID
    user_id: UUID
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""
    payment_method_id: Optional[str] = None
    type: str = Field(..., max_length=50)  # Changed from enum to string
    amount: Decimal = Field(..., decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    description: Optional[str] = None
    reference_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    status: Optional[str] = Field(None, max_length=50)  # Changed from enum to string
    description: Optional[str] = Field(None, max_length=500)


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: str
    user_id: str
    payment_method_id: Optional[str]
    type: str  # Changed from enum to string
    amount: Decimal
    currency: str
    status: str  # Changed from enum to string
    provider_transaction_id: Optional[str]
    description: Optional[str]
    reference_id: Optional[str]
    invoice_number: Optional[str]
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    payment_method_id: Optional[str] = None
    plan_name: str = Field(..., max_length=100)
    plan_description: Optional[str] = None
    billing_cycle: str = Field(..., max_length=50)  # Changed from enum to string
    amount: Decimal = Field(..., decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    trial_end_date: Optional[datetime] = None
    features: Optional[Dict[str, Any]] = None
    usage_limits: Optional[Dict[str, Any]] = None


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    payment_method_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None
    usage_limits: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, max_length=50)  # Changed from enum to string
    end_date: Optional[date] = None


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: str
    user_id: str
    payment_method_id: Optional[str]
    plan_name: str
    plan_description: Optional[str]
    billing_cycle: str  # Changed from enum to string
    amount: Decimal
    currency: str
    provider: Optional[str]
    provider_subscription_id: Optional[str]
    status: str
    trial_end_date: Optional[datetime]
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    cancelled_at: Optional[datetime]
    features: Optional[Dict[str, Any]]
    usage_limits: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Medication Cost Schemas
class MedicationCostCreate(BaseModel):
    """Schema for creating a medication cost entry."""
    medication_id: int
    cost_per_unit: Decimal = Field(..., decimal_places=2)
    quantity: int = Field(..., gt=0)
    total_cost: Decimal = Field(..., decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    pharmacy_name: Optional[str] = None
    prescription_number: Optional[str] = None
    insurance_covered: bool = False
    insurance_copay: Optional[Decimal] = Field(None, decimal_places=2)
    out_of_pocket: Optional[Decimal] = Field(None, decimal_places=2)
    purchase_date: datetime
    notes: Optional[str] = None

    @validator('total_cost')
    def validate_total_cost(cls, v, values):
        if 'cost_per_unit' in values and 'quantity' in values:
            expected_total = values['cost_per_unit'] * values['quantity']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Total cost must equal cost_per_unit * quantity')
        return v


class MedicationCostUpdate(BaseModel):
    """Schema for updating a medication cost entry."""
    cost_per_unit: Optional[Decimal] = Field(None, decimal_places=2)
    quantity: Optional[int] = Field(None, gt=0)
    total_cost: Optional[Decimal] = Field(None, decimal_places=2)
    pharmacy_name: Optional[str] = None
    prescription_number: Optional[str] = None
    insurance_covered: Optional[bool] = None
    insurance_copay: Optional[Decimal] = Field(None, decimal_places=2)
    out_of_pocket: Optional[Decimal] = Field(None, decimal_places=2)
    purchase_date: Optional[datetime] = None
    notes: Optional[str] = None


class MedicationCostResponse(BaseModel):
    """Schema for medication cost response."""
    id: str
    user_id: str
    medication_id: int
    cost_per_unit: Decimal
    quantity: int
    total_cost: Decimal
    currency: str
    pharmacy_name: Optional[str]
    prescription_number: Optional[str]
    insurance_covered: bool
    insurance_copay: Optional[Decimal]
    out_of_pocket: Optional[Decimal]
    purchase_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceLineItem(BaseModel):
    """Schema for invoice line item."""
    description: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., decimal_places=2)
    total_price: Decimal = Field(..., decimal_places=2)


class InvoiceCreate(BaseModel):
    """Schema for creating an invoice."""
    invoice_date: datetime
    due_date: Optional[datetime] = None
    line_items: List[InvoiceLineItem]
    tax_amount: Decimal = Field(default=Decimal('0.00'), decimal_places=2)
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    status: Optional[str] = Field(None, max_length=50)  # Changed from enum to string
    paid_at: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""
    id: str
    user_id: str
    transaction_id: Optional[str]
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    status: str
    paid_at: Optional[datetime]
    line_items: List[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Financial Summary Schemas
class FinancialSummaryResponse(BaseModel):
    """Schema for financial summary response."""
    total_spent: Decimal
    medication_costs: Decimal
    subscription_costs: Decimal
    consultation_fees: Decimal
    period_start: datetime
    period_end: datetime
    currency: str
    recent_transactions: List[TransactionResponse]
    active_subscriptions: List[SubscriptionResponse]

    class Config:
        from_attributes = True