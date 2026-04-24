"""Financial models for the IBS Wellness Companion application."""

import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class PaymentMethodTypeEnum(str, enum.Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class TransactionTypeEnum(str, enum.Enum):
    """Transaction types."""
    PAYMENT = "payment"
    REFUND = "refund"
    SUBSCRIPTION = "subscription"
    MEDICATION = "medication"
    CONSULTATION = "consultation"
    ADJUSTMENT = "adjustment"


class PaymentStatusEnum(str, enum.Enum):
    """Payment status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatusEnum(str, enum.Enum):
    """Subscription status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"


class BillingCycleEnum(str, enum.Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


class InvoiceStatusEnum(str, enum.Enum):
    """Invoice status values."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(Base):
    """User payment methods."""

    __tablename__ = "payment_methods"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Payment method details
    type = Column(String(50), nullable=False, index=True)  # Changed from enum
    provider = Column(String(50), nullable=False)  # Made required
    # Required provider payment method ID
    provider_payment_method_id = Column(String(255), nullable=False)

    # Card/Account details (encrypted/tokenized)
    last_four_digits = Column(String(4), nullable=True)
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    cardholder_name = Column(String(100), nullable=True)  # Added

    # Bank account details (for ACH) - Removed to match migration

    # Metadata
    is_default = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship("Transaction", back_populates="payment_method")

    def __repr__(self) -> str:
        return (
            f"<PaymentMethod(id={self.id}, user_id={self.user_id}, "
            f"type='{self.type}')>"
        )


class BillingAddress(Base):
    """User billing addresses."""

    __tablename__ = "billing_addresses"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Address details
    # Changed from address_line_1
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)  # Changed from 2-char ISO to 100 chars to match migration

    # Metadata
    is_default = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="billing_addresses")

    def __repr__(self) -> str:
        return f"<BillingAddress(id={self.id}, user_id={self.user_id}, city='{self.city}')>"


class Transaction(Base):
    """Financial transactions."""

    __tablename__ = "transactions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=True, index=True)

    # Transaction details
    type = Column(String(50), nullable=False, index=True)  # Changed from enum to string
    amount = Column(Numeric(10, 2), nullable=False)  # Amount in cents/smallest currency unit
    currency = Column(String(3), default="USD", nullable=False)  # ISO currency code

    # Payment processing
    status = Column(String(50), nullable=False, default='pending')  # Changed from enum to string
    provider_transaction_id = Column(String(255), nullable=True)  # External provider transaction ID
    provider_response = Column(JSONB, nullable=True)  # Full provider response

    # Transaction metadata
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # Internal reference
    invoice_number = Column(String(50), nullable=True)

    # Related entities (polymorphic references)
    related_entity_type = Column(String(50), nullable=True)  # "subscription", "medication", etc.
    related_entity_id = Column(String(255), nullable=True)

    # Timestamps
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"


class Subscription(Base):
    """User subscriptions for premium features."""

    __tablename__ = "subscriptions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=True, index=True)

    # Subscription details
    plan_name = Column(String(100), nullable=False)
    plan_description = Column(Text, nullable=True)
    billing_cycle = Column(String(50), nullable=False)  # Changed from enum to string
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Provider details
    provider = Column(String(50), nullable=True)  # e.g., "stripe"
    provider_subscription_id = Column(String(255), nullable=True)
    provider_customer_id = Column(String(255), nullable=True)

    # Status and lifecycle
    status = Column(String(50), nullable=False, default='active', index=True)  # Changed from enum to string
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Features and limits
    features = Column(JSONB, nullable=True)  # JSON object with feature flags
    usage_limits = Column(JSONB, nullable=True)  # JSON object with usage limits

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payment_method = relationship("PaymentMethod")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_name}', status='{self.status}')>"


class MedicationCost(Base):
    """Medication cost tracking."""

    __tablename__ = "medication_costs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False, index=True)

    # Cost details
    cost_per_unit = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Purchase details
    pharmacy_name = Column(String(200), nullable=True)
    prescription_number = Column(String(100), nullable=True)
    insurance_covered = Column(Boolean, default=False, nullable=False)
    insurance_copay = Column(Numeric(10, 2), nullable=True)
    out_of_pocket = Column(Numeric(10, 2), nullable=True)

    # Metadata
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="medication_costs")
    medication = relationship("Medication", back_populates="medication_costs")

    def __repr__(self) -> str:
        return f"<MedicationCost(id={self.id}, user_id={self.user_id}, total_cost={self.total_cost})>"


class Invoice(Base):
    """Invoices for services and purchases."""

    __tablename__ = "invoices"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True, index=True)

    # Invoice details
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')

    # Status and dates
    status = Column(String(50), nullable=False, default='draft')  # Changed from enum to string
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Invoice content
    line_items = Column(JSONB, nullable=False)  # JSON array of line items
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="invoices")
    transaction = relationship("Transaction")

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', total={self.total_amount})>"
