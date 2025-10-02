"""
Financial API

API endpoints for financial operations including payment methods, transactions,
subscriptions, and medication cost tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.financial import (
    PaymentMethod,
    BillingAddress,
    Transaction,
    Subscription,
    MedicationCost,
    Invoice,
)
from app.models.medication import Medication
from app.schemas.financial import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    BillingAddressCreate,
    BillingAddressUpdate,
    BillingAddressResponse,
    TransactionCreate,
    TransactionResponse,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    MedicationCostCreate,
    MedicationCostUpdate,
    MedicationCostResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    FinancialSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Financial"])


# Payment Methods
@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(
    payment_method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new payment method for the user."""
    try:
        # If this is set as default, unset other default payment methods
        if payment_method_data.is_default:
            stmt = select(PaymentMethod).where(
                and_(
                    PaymentMethod.user_id == current_user.id,
                    PaymentMethod.is_default is True,
                )
            )
            result = await db.execute(stmt)
            existing_defaults = result.scalars().all()

            for pm in existing_defaults:
                pm.is_default = False

        # Create new payment method
        payment_method = PaymentMethod(
            user_id=current_user.id, **payment_method_data.dict()
        )

        db.add(payment_method)
        await db.commit()
        await db.refresh(payment_method)

        return payment_method

    except Exception as e:
        logger.error(f"Error creating payment method: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment method",
        )


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all payment methods for the current user."""
    try:
        stmt = (
            select(PaymentMethod)
            .where(PaymentMethod.user_id == current_user.id)
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
        )

        result = await db.execute(stmt)
        payment_methods = result.scalars().all()

        return payment_methods

    except Exception as e:
        logger.error(f"Error fetching payment methods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment methods",
        )


@router.put(
    "/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse
)
async def update_payment_method(
    payment_method_id: str,
    payment_method_data: PaymentMethodUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a payment method."""
    try:
        stmt = select(PaymentMethod).where(
            and_(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.user_id == current_user.id,
            )
        )
        result = await db.execute(stmt)
        payment_method = result.scalar_one_or_none()

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found"
            )

        # If setting as default, unset other defaults
        if payment_method_data.is_default:
            stmt = select(PaymentMethod).where(
                and_(
                    PaymentMethod.user_id == current_user.id,
                    PaymentMethod.is_default is True,
                    PaymentMethod.id != payment_method_id,
                )
            )
            result = await db.execute(stmt)
            existing_defaults = result.scalars().all()

            for pm in existing_defaults:
                pm.is_default = False

        # Update payment method
        for field, value in payment_method_data.dict(exclude_unset=True).items():
            setattr(payment_method, field, value)

        await db.commit()
        await db.refresh(payment_method)

        return payment_method

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payment method: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment method",
        )


@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) a payment method."""
    try:
        stmt = select(PaymentMethod).where(
            and_(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.user_id == current_user.id,
            )
        )
        result = await db.execute(stmt)
        payment_method = result.scalar_one_or_none()

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found"
            )

        # Simply delete the payment method from database
        await db.delete(payment_method)
        await db.commit()

        return {"message": "Payment method deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting payment method: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment method",
        )


# Billing Addresses
@router.post("/billing-addresses", response_model=BillingAddressResponse)
async def create_billing_address(
    address_data: BillingAddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new billing address for the user."""
    try:
        # If this is set as default, unset other default addresses
        if address_data.is_default:
            stmt = select(BillingAddress).where(
                and_(
                    BillingAddress.user_id == current_user.id,
                    BillingAddress.is_default is True,
                    BillingAddress.is_active is True,
                )
            )
            result = await db.execute(stmt)
            existing_defaults = result.scalars().all()

            for addr in existing_defaults:
                addr.is_default = False

        # Create new billing address
        billing_address = BillingAddress(user_id=current_user.id, **address_data.dict())

        db.add(billing_address)
        await db.commit()
        await db.refresh(billing_address)

        return billing_address

    except Exception as e:
        logger.error(f"Error creating billing address: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing address",
        )


@router.get("/billing-addresses", response_model=List[BillingAddressResponse])
async def get_billing_addresses(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all billing addresses for the current user."""
    try:
        stmt = (
            select(BillingAddress)
            .where(
                and_(
                    BillingAddress.user_id == current_user.id,
                    BillingAddress.is_active is True,
                )
            )
            .order_by(
                BillingAddress.is_default.desc(), BillingAddress.created_at.desc()
            )
        )

        result = await db.execute(stmt)
        addresses = result.scalars().all()

        return addresses

    except Exception as e:
        logger.error(f"Error fetching billing addresses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch billing addresses",
        )


# Transactions
@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new transaction."""
    try:
        # Validate payment method belongs to user if provided
        if transaction_data.payment_method_id:
            stmt = select(PaymentMethod).where(
                and_(
                    PaymentMethod.id == transaction_data.payment_method_id,
                    PaymentMethod.user_id == current_user.id,
                    PaymentMethod.is_active is True,
                )
            )
            result = await db.execute(stmt)
            payment_method = result.scalar_one_or_none()

            if not payment_method:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment method not found",
                )

        # Create transaction
        transaction = Transaction(
            user_id=current_user.id, status="pending", **transaction_data.dict()
        )

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction",
        )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    transaction_type: Optional[str] = None,  # Changed from enum to string
    status: Optional[str] = None,  # Changed from enum to string
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transactions for the current user."""
    try:
        stmt = select(Transaction).where(Transaction.user_id == current_user.id)

        if transaction_type:
            stmt = stmt.where(Transaction.type == transaction_type)

        if status:
            stmt = stmt.where(Transaction.status == status)

        stmt = stmt.order_by(desc(Transaction.created_at)).limit(limit).offset(offset)

        result = await db.execute(stmt)
        transactions = result.scalars().all()

        return transactions

    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions",
        )


# Subscription Management
@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new subscription."""
    try:
        # Validate payment method if provided
        if subscription_data.payment_method_id:
            stmt = select(PaymentMethod).where(
                and_(
                    PaymentMethod.id == subscription_data.payment_method_id,
                    PaymentMethod.user_id == current_user.id,
                )
            )
            result = await db.execute(stmt)
            payment_method = result.scalar_one_or_none()

            if not payment_method:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment method not found",
                )

        # Create subscription
        subscription = Subscription(user_id=current_user.id, **subscription_data.dict())

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        return subscription

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription",
        )


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get subscriptions for the current user."""
    try:
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == current_user.id)
            .order_by(desc(Subscription.created_at))
        )

        result = await db.execute(stmt)
        subscriptions = result.scalars().all()

        return subscriptions

    except Exception as e:
        logger.error(f"Error fetching subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscriptions",
        )


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a subscription."""
    try:
        stmt = select(Subscription).where(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == current_user.id,
            )
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
            )

        # Update subscription
        for field, value in subscription_data.dict(exclude_unset=True).items():
            setattr(subscription, field, value)

        await db.commit()
        await db.refresh(subscription)

        return subscription

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription",
        )


@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a subscription."""
    try:
        stmt = select(Subscription).where(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == current_user.id,
            )
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
            )

        # Cancel subscription
        subscription.status = "cancelled"
        subscription.end_date = datetime.utcnow().date()

        await db.commit()

        return {"message": "Subscription cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )


# Invoice Management
@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new invoice."""
    try:
        # Create invoice
        invoice = Invoice(user_id=current_user.id, **invoice_data.dict())

        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)

        return invoice

    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invoice",
        )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get invoices for the current user."""
    try:
        stmt = select(Invoice).where(Invoice.user_id == current_user.id)

        if status:
            stmt = stmt.where(Invoice.status == status)

        stmt = stmt.order_by(desc(Invoice.created_at))

        result = await db.execute(stmt)
        invoices = result.scalars().all()

        return invoices

    except Exception as e:
        logger.error(f"Error fetching invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch invoices",
        )


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific invoice."""
    try:
        stmt = select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )

        return invoice

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch invoice",
        )


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an invoice."""
    try:
        stmt = select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )

        # Update invoice
        for field, value in invoice_data.dict(exclude_unset=True).items():
            setattr(invoice, field, value)

        await db.commit()
        await db.refresh(invoice)

        return invoice

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating invoice: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invoice",
        )


# Medication Costs
@router.post("/medication-costs", response_model=MedicationCostResponse)
async def create_medication_cost(
    cost_data: MedicationCostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new medication cost entry."""
    try:
        # Validate medication exists
        stmt = select(Medication).where(Medication.id == cost_data.medication_id)
        result = await db.execute(stmt)
        medication = result.scalar_one_or_none()

        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found"
            )

        # Create medication cost
        medication_cost = MedicationCost(user_id=current_user.id, **cost_data.dict())

        db.add(medication_cost)
        await db.commit()
        await db.refresh(medication_cost)

        return medication_cost

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating medication cost: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medication cost",
        )


@router.get("/medication-costs", response_model=List[MedicationCostResponse])
async def get_medication_costs(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    medication_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get medication costs for the current user."""
    try:
        stmt = select(MedicationCost).where(MedicationCost.user_id == current_user.id)

        if medication_id:
            stmt = stmt.where(MedicationCost.medication_id == medication_id)

        stmt = (
            stmt.order_by(desc(MedicationCost.purchase_date))
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(stmt)
        costs = result.scalars().all()

        return costs

    except Exception as e:
        logger.error(f"Error fetching medication costs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medication costs",
        )


# Financial Summary
@router.get("/summary", response_model=FinancialSummaryResponse)
async def get_financial_summary(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get financial summary for the current user."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get total spent in period
        stmt = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.status == "completed",
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
            )
        )
        result = await db.execute(stmt)
        total_spent = result.scalar() or Decimal("0.00")

        # Get medication costs
        stmt = select(func.sum(MedicationCost.total_cost)).where(
            and_(
                MedicationCost.user_id == current_user.id,
                MedicationCost.purchase_date >= start_date,
                MedicationCost.purchase_date <= end_date,
            )
        )
        result = await db.execute(stmt)
        medication_costs = result.scalar() or Decimal("0.00")

        # Get subscription costs
        stmt = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.type == "subscription",
                Transaction.status == "completed",
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
            )
        )
        result = await db.execute(stmt)
        subscription_costs = result.scalar() or Decimal("0.00")

        # Get consultation fees
        stmt = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.type == "consultation_fee",
                Transaction.status == "completed",
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
            )
        )
        result = await db.execute(stmt)
        consultation_fees = result.scalar() or Decimal("0.00")

        # Get recent transactions
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == current_user.id)
            .order_by(desc(Transaction.created_at))
            .limit(10)
        )
        result = await db.execute(stmt)
        recent_transactions = result.scalars().all()

        # Get active subscriptions
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == current_user.id, Subscription.status == "active"
            )
        )
        result = await db.execute(stmt)
        active_subscriptions = result.scalars().all()

        return FinancialSummaryResponse(
            total_spent=total_spent,
            medication_costs=medication_costs,
            subscription_costs=subscription_costs,
            consultation_fees=consultation_fees,
            period_start=start_date,
            period_end=end_date,
            currency="USD",
            recent_transactions=recent_transactions,
            active_subscriptions=active_subscriptions,
        )

    except Exception as e:
        logger.error(f"Error generating financial summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial summary",
        )
