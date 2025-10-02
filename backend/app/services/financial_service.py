"""
Financial Service

Business logic for financial operations including payment processing,
subscription management, and cost tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from app.models.financial import (
    PaymentMethod,
    Transaction,
    Subscription,
    MedicationCost,
    Invoice,
    PaymentStatusEnum,
    TransactionTypeEnum,
    SubscriptionStatusEnum,
)
from app.models.medication import Medication

logger = logging.getLogger(__name__)


class FinancialService:
    """Service class for financial operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_payment(
        self,
        user_id: str,
        amount: Decimal,
        transaction_type: TransactionTypeEnum,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Transaction:
        """Process a payment transaction."""
        try:
            # Get default payment method if none specified
            if not payment_method_id:
                stmt = select(PaymentMethod).where(
                    and_(
                         PaymentMethod.user_id == user_id,
                         PaymentMethod.is_default.is_(True),
                         PaymentMethod.is_active.is_(True),
                     )
                )
                result = await self.db.execute(stmt)
                payment_method = result.scalar_one_or_none()

                if not payment_method:
                    raise ValueError("No default payment method found")

                payment_method_id = payment_method.id

            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                payment_method_id=payment_method_id,
                amount=amount,
                transaction_type=transaction_type,
                status=PaymentStatusEnum.PENDING,
                description=description,
                metadata=metadata or {},
            )

            self.db.add(transaction)
            await self.db.flush()

            # Simulate payment processing
            # In a real implementation, this would integrate with payment providers
            success = await self._simulate_payment_processing(transaction)

            if success:
                transaction.status = PaymentStatusEnum.COMPLETED
                transaction.processed_at = datetime.utcnow()
            else:
                transaction.status = PaymentStatusEnum.FAILED
                transaction.failure_reason = "Payment processing failed"

            await self.db.commit()
            await self.db.refresh(transaction)

            return transaction

        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            await self.db.rollback()
            raise

    async def _simulate_payment_processing(self, transaction: Transaction) -> bool:
        """Simulate payment processing (replace with real payment gateway)."""
        # In a real implementation, this would call external payment APIs
        # For now, we'll simulate a 95% success rate
        import random

        return random.random() < 0.95

    async def create_subscription(
        self,
        user_id: str,
        plan_name: str,
        amount: Decimal,
        billing_cycle: str,
        payment_method_id: Optional[str] = None,
    ) -> Subscription:
        """Create a new subscription."""
        try:
            # Calculate next billing date
            next_billing_date = self._calculate_next_billing_date(billing_cycle)

            # Create subscription
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                plan_name=plan_name,
                amount=amount,
                billing_cycle=billing_cycle,
                status=SubscriptionStatusEnum.ACTIVE,
                next_billing_date=next_billing_date,
                payment_method_id=payment_method_id,
            )

            self.db.add(subscription)

            # Process initial payment
            initial_transaction = await self.process_payment(
                user_id=user_id,
                amount=amount,
                transaction_type=TransactionTypeEnum.SUBSCRIPTION,
                payment_method_id=payment_method_id,
                description=f"Initial payment for {plan_name} subscription",
            )

            subscription.last_payment_transaction_id = initial_transaction.id

            await self.db.commit()
            await self.db.refresh(subscription)

            return subscription

        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            await self.db.rollback()
            raise

    def _calculate_next_billing_date(self, billing_cycle: str) -> datetime:
        """Calculate the next billing date based on billing cycle."""
        now = datetime.utcnow()

        if billing_cycle == "monthly":
            return now + timedelta(days=30)
        elif billing_cycle == "quarterly":
            return now + timedelta(days=90)
        elif billing_cycle == "yearly":
            return now + timedelta(days=365)
        else:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")

    async def cancel_subscription(
        self, subscription_id: str, user_id: str
    ) -> Subscription:
        """Cancel a subscription."""
        try:
            stmt = select(Subscription).where(
                and_(
                    Subscription.id == subscription_id, Subscription.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise ValueError("Subscription not found")

            subscription.status = SubscriptionStatusEnum.CANCELLED
            subscription.cancelled_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(subscription)

            return subscription

        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            await self.db.rollback()
            raise

    async def track_medication_cost(
        self,
        user_id: str,
        medication_id: int,
        pharmacy_name: str,
        unit_cost: Decimal,
        quantity: int,
        insurance_covered: bool = False,
        insurance_copay: Optional[Decimal] = None,
    ) -> MedicationCost:
        """Track medication cost."""
        try:
            total_cost = unit_cost * quantity
            out_of_pocket = total_cost

            if insurance_covered and insurance_copay:
                out_of_pocket = insurance_copay

            medication_cost = MedicationCost(
                id=str(uuid.uuid4()),
                user_id=user_id,
                medication_id=medication_id,
                pharmacy_name=pharmacy_name,
                unit_cost=unit_cost,
                quantity=quantity,
                total_cost=total_cost,
                insurance_covered=insurance_covered,
                insurance_copay=insurance_copay,
                out_of_pocket_cost=out_of_pocket,
                purchase_date=datetime.utcnow(),
            )

            self.db.add(medication_cost)
            await self.db.commit()
            await self.db.refresh(medication_cost)

            return medication_cost

        except Exception as e:
            logger.error(f"Error tracking medication cost: {str(e)}")
            await self.db.rollback()
            raise

    async def generate_invoice(
        self,
        user_id: str,
        transaction_ids: List[str],
        billing_address_id: Optional[str] = None,
    ) -> Invoice:
        """Generate an invoice for transactions."""
        try:
            # Get transactions
            stmt = select(Transaction).where(
                and_(
                    Transaction.id.in_(transaction_ids),
                    Transaction.user_id == user_id,
                    Transaction.status == PaymentStatusEnum.COMPLETED,
                )
            )
            result = await self.db.execute(stmt)
            transactions = result.scalars().all()

            if not transactions:
                raise ValueError("No valid transactions found")

            # Calculate totals
            subtotal = sum(t.amount for t in transactions)
            tax_amount = subtotal * Decimal("0.08")  # 8% tax rate
            total_amount = subtotal + tax_amount

            # Create invoice
            invoice = Invoice(
                id=str(uuid.uuid4()),
                user_id=user_id,
                invoice_number=self._generate_invoice_number(),
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                billing_address_id=billing_address_id,
                status="generated",
                issue_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
            )

            self.db.add(invoice)
            await self.db.flush()

            # Link transactions to invoice
            for transaction in transactions:
                transaction.invoice_id = invoice.id

            await self.db.commit()
            await self.db.refresh(invoice)

            return invoice

        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            await self.db.rollback()
            raise

    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{random_suffix}"

    async def get_spending_analytics(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get spending analytics for a user."""
        try:
            # Total spending by category
            stmt = (
                select(
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label("total"),
                )
                .where(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.status == PaymentStatusEnum.COMPLETED,
                        Transaction.created_at >= start_date,
                        Transaction.created_at <= end_date,
                    )
                )
                .group_by(Transaction.transaction_type)
            )

            result = await self.db.execute(stmt)
            spending_by_category = {row.transaction_type: row.total for row in result}

            # Monthly spending trend
            stmt = (
                select(
                    func.date_trunc("month", Transaction.created_at).label("month"),
                    func.sum(Transaction.amount).label("total"),
                )
                .where(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.status == PaymentStatusEnum.COMPLETED,
                        Transaction.created_at >= start_date,
                        Transaction.created_at <= end_date,
                    )
                )
                .group_by(func.date_trunc("month", Transaction.created_at))
                .order_by("month")
            )

            result = await self.db.execute(stmt)
            monthly_trend = [
                {"month": row.month.strftime("%Y-%m"), "total": row.total}
                for row in result
            ]

            # Top medications by cost
            stmt = (
                select(
                    Medication.name,
                    func.sum(MedicationCost.out_of_pocket_cost).label("total_cost"),
                )
                .join(MedicationCost, Medication.id == MedicationCost.medication_id)
                .where(
                    and_(
                        MedicationCost.user_id == user_id,
                        MedicationCost.purchase_date >= start_date,
                        MedicationCost.purchase_date <= end_date,
                    )
                )
                .group_by(Medication.name)
                .order_by(desc("total_cost"))
                .limit(10)
            )

            result = await self.db.execute(stmt)
            top_medications = [
                {"medication": row.name, "total_cost": row.total_cost} for row in result
            ]

            return {
                "spending_by_category": spending_by_category,
                "monthly_trend": monthly_trend,
                "top_medications": top_medications,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting spending analytics: {str(e)}")
            raise

    async def process_recurring_subscriptions(self) -> List[Dict[str, Any]]:
        """Process recurring subscription payments."""
        try:
            # Find subscriptions due for billing
            now = datetime.utcnow()
            stmt = select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatusEnum.ACTIVE,
                    Subscription.next_billing_date <= now,
                )
            )

            result = await self.db.execute(stmt)
            due_subscriptions = result.scalars().all()

            processed_results = []

            for subscription in due_subscriptions:
                try:
                    # Process payment
                    transaction = await self.process_payment(
                        user_id=subscription.user_id,
                        amount=subscription.amount,
                        transaction_type=TransactionTypeEnum.SUBSCRIPTION,
                        payment_method_id=subscription.payment_method_id,
                        description=f"Recurring payment for {subscription.plan_name}",
                    )

                    if transaction.status == PaymentStatusEnum.COMPLETED:
                        # Update subscription
                        subscription.last_payment_transaction_id = transaction.id
                        subscription.next_billing_date = (
                            self._calculate_next_billing_date(
                                subscription.billing_cycle
                            )
                        )

                        processed_results.append(
                            {
                                "subscription_id": subscription.id,
                                "status": "success",
                                "transaction_id": transaction.id,
                            }
                        )
                    else:
                        # Handle failed payment
                        subscription.failed_payment_count += 1

                        if subscription.failed_payment_count >= 3:
                            subscription.status = SubscriptionStatusEnum.SUSPENDED

                        processed_results.append(
                            {
                                "subscription_id": subscription.id,
                                "status": "failed",
                                "reason": transaction.failure_reason,
                            }
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing subscription {subscription.id}: {str(e)}"
                    )
                    processed_results.append(
                        {
                            "subscription_id": subscription.id,
                            "status": "error",
                            "reason": str(e),
                        }
                    )

            await self.db.commit()
            return processed_results

        except Exception as e:
            logger.error(f"Error processing recurring subscriptions: {str(e)}")
            await self.db.rollback()
            raise
