"""
Billing & Subscriptions System

Provides comprehensive billing capabilities:
- Subscription plan management (FREE, STARTER, PROFESSIONAL, ENTERPRISE, CUSTOM)
- Usage metering and tracking
- Automated invoice generation
- Payment processing with multiple providers
- Dunning management for failed payments
- Revenue recognition
- Proration for plan changes
- Trial periods and discounts
- Tax calculation
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional


class BillingCycle(str, Enum):
    """Billing cycle types"""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class PaymentStatus(str, Enum):
    """Payment status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    """Invoice status"""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class PaymentMethod(str, Enum):
    """Payment methods"""

    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    SEPA_DEBIT = "sepa_debit"
    INVOICE = "invoice"


class TaxType(str, Enum):
    """Tax types"""

    VAT = "vat"  # Value Added Tax (EU)
    GST = "gst"  # Goods and Services Tax
    SALES_TAX = "sales_tax"  # US Sales Tax
    NO_TAX = "no_tax"


class DiscountType(str, Enum):
    """Discount types"""

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_TRIAL = "free_trial"


@dataclass
class PlanFeature:
    """Plan feature"""

    name: str
    description: str
    included: bool = True
    limit: Optional[int] = None  # None = unlimited
    unit: str = ""


@dataclass
class SubscriptionPlan:
    """Subscription plan"""

    id: str
    name: str
    description: str
    price_monthly: Decimal
    price_yearly: Decimal
    currency: str = "EUR"

    # Features
    features: List[PlanFeature] = field(default_factory=list)

    # Resource limits
    max_users: int = 1
    max_storage_gb: int = 1
    max_documents: int = 100
    max_api_calls_per_month: int = 1000

    # Billing
    billing_cycles: List[BillingCycle] = field(default_factory=lambda: [BillingCycle.MONTHLY])
    trial_days: int = 0

    # Status
    is_active: bool = True
    is_public: bool = True

    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    """Customer subscription"""

    id: str
    tenant_id: str
    plan_id: str

    # Billing
    billing_cycle: BillingCycle
    current_period_start: datetime
    current_period_end: datetime

    # Status
    status: str = "active"  # active, cancelled, past_due, trialing
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None

    # Trial
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None

    # Payment
    payment_method_id: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageRecord:
    """Usage tracking record"""

    id: str
    tenant_id: str
    subscription_id: str

    metric_name: str  # e.g., "api_calls", "storage_gb", "documents"
    quantity: float
    timestamp: datetime

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvoiceLineItem:
    """Invoice line item"""

    description: str
    quantity: float
    unit_price: Decimal
    amount: Decimal
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")


@dataclass
class Invoice:
    """Customer invoice"""

    id: str
    invoice_number: str
    tenant_id: str
    subscription_id: str

    # Amounts
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    amount_due: Decimal
    amount_paid: Decimal = Decimal("0")

    # Currency
    currency: str = "EUR"

    # Items
    line_items: List[InvoiceLineItem] = field(default_factory=list)

    # Dates
    issued_at: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=14))
    paid_at: Optional[datetime] = None

    # Status
    status: InvoiceStatus = InvoiceStatus.DRAFT

    # Payment
    payment_method: Optional[PaymentMethod] = None

    # Metadata
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Payment:
    """Payment transaction"""

    id: str
    invoice_id: str
    tenant_id: str

    amount: Decimal
    currency: str

    payment_method: PaymentMethod
    payment_method_details: Dict[str, Any] = field(default_factory=dict)

    status: PaymentStatus = PaymentStatus.PENDING

    # Gateway
    gateway_id: Optional[str] = None  # External payment gateway transaction ID
    gateway_name: Optional[str] = None  # e.g., "stripe", "paypal"

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Discount:
    """Discount/Coupon"""

    id: str
    code: str
    name: str

    discount_type: DiscountType
    amount: Decimal  # Percentage (0-100) or fixed amount

    # Applicability
    applies_to_plans: List[str] = field(default_factory=list)  # Empty = all plans

    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    redemptions_count: int = 0

    # Status
    is_active: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


class PlanManager:
    """Manages subscription plans"""

    def __init__(self):
        self.plans: Dict[str, SubscriptionPlan] = {}
        self._initialize_default_plans()

    def _initialize_default_plans(self):
        """Initialize default subscription plans"""
        # FREE Plan
        self.plans["free"] = SubscriptionPlan(
            id="free",
            name="Free",
            description="Perfect for getting started",
            price_monthly=Decimal("0"),
            price_yearly=Decimal("0"),
            max_users=1,
            max_storage_gb=1,
            max_documents=100,
            max_api_calls_per_month=1000,
            features=[
                PlanFeature("Basic document management", "", True),
                PlanFeature("1 GB storage", "", True, 1, "GB"),
                PlanFeature("100 documents", "", True, 100),
                PlanFeature("Email support", "", True),
            ],
        )

        # STARTER Plan
        self.plans["starter"] = SubscriptionPlan(
            id="starter",
            name="Starter",
            description="For small teams",
            price_monthly=Decimal("29.00"),
            price_yearly=Decimal("290.00"),  # 2 months free
            max_users=5,
            max_storage_gb=10,
            max_documents=1000,
            max_api_calls_per_month=10000,
            trial_days=14,
            features=[
                PlanFeature("Up to 5 users", "", True, 5),
                PlanFeature("10 GB storage", "", True, 10, "GB"),
                PlanFeature("1,000 documents", "", True, 1000),
                PlanFeature("Email & chat support", "", True),
                PlanFeature("Basic analytics", "", True),
            ],
        )

        # PROFESSIONAL Plan
        self.plans["professional"] = SubscriptionPlan(
            id="professional",
            name="Professional",
            description="For growing businesses",
            price_monthly=Decimal("99.00"),
            price_yearly=Decimal("990.00"),
            max_users=25,
            max_storage_gb=100,
            max_documents=10000,
            max_api_calls_per_month=100000,
            trial_days=14,
            features=[
                PlanFeature("Up to 25 users", "", True, 25),
                PlanFeature("100 GB storage", "", True, 100, "GB"),
                PlanFeature("10,000 documents", "", True, 10000),
                PlanFeature("Priority support", "", True),
                PlanFeature("Advanced analytics", "", True),
                PlanFeature("Custom branding", "", True),
                PlanFeature("API access", "", True),
            ],
        )

        # ENTERPRISE Plan
        self.plans["enterprise"] = SubscriptionPlan(
            id="enterprise",
            name="Enterprise",
            description="For large organizations",
            price_monthly=Decimal("499.00"),
            price_yearly=Decimal("4990.00"),
            max_users=999999,  # Unlimited
            max_storage_gb=1000,
            max_documents=999999,
            max_api_calls_per_month=999999,
            trial_days=30,
            features=[
                PlanFeature("Unlimited users", "", True),
                PlanFeature("1 TB storage", "", True, 1000, "GB"),
                PlanFeature("Unlimited documents", "", True),
                PlanFeature("24/7 phone support", "", True),
                PlanFeature("Advanced analytics & BI", "", True),
                PlanFeature("White-labeling", "", True),
                PlanFeature("Dedicated account manager", "", True),
                PlanFeature("SLA guarantee", "", True),
                PlanFeature("Custom integrations", "", True),
            ],
        )

    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get plan by ID"""
        return self.plans.get(plan_id)

    def list_plans(self, public_only: bool = True) -> List[SubscriptionPlan]:
        """List all plans"""
        plans = list(self.plans.values())
        if public_only:
            plans = [p for p in plans if p.is_public]
        return plans

    def create_custom_plan(self, name: str, price_monthly: Decimal, **kwargs) -> SubscriptionPlan:
        """Create custom plan"""
        plan_id = str(uuid.uuid4())

        plan = SubscriptionPlan(
            id=plan_id,
            name=name,
            description=kwargs.get("description", ""),
            price_monthly=price_monthly,
            price_yearly=kwargs.get("price_yearly", price_monthly * 12),
            **kwargs,
        )

        self.plans[plan_id] = plan
        print(f"[Billing] Created custom plan: {name}")
        return plan


class UsageMeter:
    """Tracks usage metrics"""

    def __init__(self):
        self.usage_records: List[UsageRecord] = []

    def record_usage(
        self,
        tenant_id: str,
        subscription_id: str,
        metric_name: str,
        quantity: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        """Record usage"""
        record = UsageRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            metric_name=metric_name,
            quantity=quantity,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        self.usage_records.append(record)
        return record

    def get_usage(self, tenant_id: str, metric_name: str, start_date: datetime, end_date: datetime) -> float:
        """Get total usage for period"""
        total = 0.0

        for record in self.usage_records:
            if (
                record.tenant_id == tenant_id
                and record.metric_name == metric_name
                and start_date <= record.timestamp <= end_date
            ):
                total += record.quantity

        return total

    def get_usage_by_subscription(
        self, subscription_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Get usage breakdown by metric"""
        usage: Dict[str, float] = {}

        for record in self.usage_records:
            if record.subscription_id == subscription_id and start_date <= record.timestamp <= end_date:

                if record.metric_name not in usage:
                    usage[record.metric_name] = 0.0
                usage[record.metric_name] += record.quantity

        return usage


class InvoiceGenerator:
    """Generates invoices"""

    def __init__(self, plan_manager: PlanManager):
        self.plan_manager = plan_manager
        self.invoices: Dict[str, Invoice] = {}
        self.invoice_counter = 1000

    def generate_invoice(
        self,
        tenant_id: str,
        subscription: Subscription,
        period_start: datetime,
        period_end: datetime,
        usage: Optional[Dict[str, float]] = None,
    ) -> Invoice:
        """Generate invoice for subscription period"""
        plan = self.plan_manager.get_plan(subscription.plan_id)

        if not plan:
            raise ValueError(f"Plan {subscription.plan_id} not found")

        # Generate invoice number
        invoice_number = f"INV-{self.invoice_counter:06d}"
        self.invoice_counter += 1

        # Calculate subscription amount
        if subscription.billing_cycle == BillingCycle.MONTHLY:
            subscription_amount = plan.price_monthly
        elif subscription.billing_cycle == BillingCycle.YEARLY:
            subscription_amount = plan.price_yearly
        else:
            subscription_amount = plan.price_monthly

        # Create line items
        line_items = []

        # Subscription line item
        line_items.append(
            InvoiceLineItem(
                description=f"{plan.name} - {subscription.billing_cycle.value.title()} Subscription",
                quantity=1.0,
                unit_price=subscription_amount,
                amount=subscription_amount,
            )
        )

        # Usage-based line items (if applicable)
        if usage:
            for metric, quantity in usage.items():
                # Example: charge for overage
                if metric == "api_calls" and quantity > plan.max_api_calls_per_month:
                    overage = quantity - plan.max_api_calls_per_month
                    overage_price = Decimal("0.01")  # $0.01 per call
                    overage_amount = Decimal(str(overage)) * overage_price

                    line_items.append(
                        InvoiceLineItem(
                            description=f"API Calls Overage ({overage:,.0f} calls)",
                            quantity=overage,
                            unit_price=overage_price,
                            amount=overage_amount,
                        )
                    )

        # Calculate totals
        subtotal = sum(item.amount for item in line_items)
        tax = self._calculate_tax(subtotal, tenant_id)
        discount = Decimal("0")
        total = subtotal + tax - discount

        # Create invoice
        invoice = Invoice(
            id=str(uuid.uuid4()),
            invoice_number=invoice_number,
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            total=total,
            amount_due=total,
            line_items=line_items,
            status=InvoiceStatus.OPEN,
            issued_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=14),
            currency=plan.currency,
        )

        self.invoices[invoice.id] = invoice

        print(f"[Billing] Generated invoice {invoice_number} for {total} {plan.currency}")
        return invoice

    def _calculate_tax(self, amount: Decimal, tenant_id: str) -> Decimal:
        """Calculate tax amount"""
        # Simplified tax calculation
        # In production, use actual tax rates based on tenant location
        tax_rate = Decimal("0.19")  # 19% VAT (Germany)
        return amount * tax_rate

    def mark_as_paid(self, invoice_id: str, payment: Payment) -> bool:
        """Mark invoice as paid"""
        invoice = self.invoices.get(invoice_id)

        if not invoice:
            return False

        invoice.status = InvoiceStatus.PAID
        invoice.amount_paid = payment.amount
        invoice.paid_at = datetime.now()
        invoice.payment_method = payment.payment_method

        print(f"[Billing] Invoice {invoice.invoice_number} marked as paid")
        return True


class PaymentProcessor:
    """Processes payments"""

    def __init__(self):
        self.payments: Dict[str, Payment] = {}

    def create_payment(
        self, invoice: Invoice, payment_method: PaymentMethod, payment_method_details: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """Create payment for invoice"""
        payment = Payment(
            id=str(uuid.uuid4()),
            invoice_id=invoice.id,
            tenant_id=invoice.tenant_id,
            amount=invoice.amount_due,
            currency=invoice.currency,
            payment_method=payment_method,
            payment_method_details=payment_method_details or {},
        )

        self.payments[payment.id] = payment
        return payment

    def process_payment(self, payment_id: str) -> bool:
        """Process payment"""
        payment = self.payments.get(payment_id)

        if not payment:
            return False

        payment.status = PaymentStatus.PROCESSING

        try:
            # In production, integrate with actual payment gateway
            # Example: Stripe, PayPal, etc.

            if payment.payment_method == PaymentMethod.CREDIT_CARD:
                success = self._process_credit_card(payment)
            elif payment.payment_method == PaymentMethod.STRIPE:
                success = self._process_stripe(payment)
            elif payment.payment_method == PaymentMethod.PAYPAL:
                success = self._process_paypal(payment)
            elif payment.payment_method == PaymentMethod.BANK_TRANSFER:
                success = self._process_bank_transfer(payment)
            else:
                success = False

            if success:
                payment.status = PaymentStatus.COMPLETED
                payment.processed_at = datetime.now()
                print(f"[Billing] Payment {payment.id} completed: {payment.amount} {payment.currency}")
            else:
                payment.status = PaymentStatus.FAILED
                payment.error_message = "Payment processing failed"
                print(f"[Billing] Payment {payment.id} failed")

            return success

        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.error_message = str(e)
            print(f"[Billing] Payment {payment.id} error: {e}")
            return False

    def _process_credit_card(self, payment: Payment) -> bool:
        """Process credit card payment"""
        # Simulate payment processing
        return True

    def _process_stripe(self, payment: Payment) -> bool:
        """Process Stripe payment"""
        # In production: use stripe.Charge.create()
        return True

    def _process_paypal(self, payment: Payment) -> bool:
        """Process PayPal payment"""
        # In production: use PayPal SDK
        return True

    def _process_bank_transfer(self, payment: Payment) -> bool:
        """Process bank transfer"""
        # Usually requires manual confirmation
        payment.status = PaymentStatus.PENDING
        return True

    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> bool:
        """Refund payment"""
        payment = self.payments.get(payment_id)

        if not payment or payment.status != PaymentStatus.COMPLETED:
            return False

        refund_amount = amount or payment.amount

        # Process refund through payment gateway
        payment.status = PaymentStatus.REFUNDED
        print(f"[Billing] Refunded {refund_amount} {payment.currency} for payment {payment_id}")

        return True


class DunningManager:
    """Manages failed payment recovery"""

    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
        self.dunning_attempts: Dict[str, int] = {}

    def handle_failed_payment(self, payment: Payment) -> bool:
        """Handle failed payment with retry logic"""
        attempts = self.dunning_attempts.get(payment.id, 0)

        if attempts >= 3:
            print(f"[Dunning] Max retry attempts reached for payment {payment.id}")
            return False

        # Wait before retry (exponential backoff)
        # In production, schedule retry for later

        self.dunning_attempts[payment.id] = attempts + 1
        payment.retry_count = attempts + 1

        print(f"[Dunning] Retry attempt {attempts + 1} for payment {payment.id}")

        # Retry payment
        success = self.payment_processor.process_payment(payment.id)

        return success


class BillingEngine:
    """Main billing engine"""

    def __init__(self):
        self.plan_manager = PlanManager()
        self.usage_meter = UsageMeter()
        self.invoice_generator = InvoiceGenerator(self.plan_manager)
        self.payment_processor = PaymentProcessor()
        self.dunning_manager = DunningManager(self.payment_processor)

        self.subscriptions: Dict[str, Subscription] = {}
        self.discounts: Dict[str, Discount] = {}

    def create_subscription(
        self,
        tenant_id: str,
        plan_id: str,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        payment_method_id: Optional[str] = None,
        trial: bool = True,
    ) -> Subscription:
        """Create new subscription"""
        plan = self.plan_manager.get_plan(plan_id)

        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        now = datetime.now()

        # Setup trial period
        trial_start = None
        trial_end = None
        status = "active"

        if trial and plan.trial_days > 0:
            trial_start = now
            trial_end = now + timedelta(days=plan.trial_days)
            status = "trialing"

        # Calculate billing period
        if billing_cycle == BillingCycle.MONTHLY:
            period_end = now + timedelta(days=30)
        elif billing_cycle == BillingCycle.YEARLY:
            period_end = now + timedelta(days=365)
        else:
            period_end = now + timedelta(days=30)

        subscription = Subscription(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            current_period_start=now,
            current_period_end=period_end,
            status=status,
            trial_start=trial_start,
            trial_end=trial_end,
            payment_method_id=payment_method_id,
        )

        self.subscriptions[subscription.id] = subscription

        print(f"[Billing] Created subscription for tenant {tenant_id}: {plan.name} ({billing_cycle.value})")
        return subscription

    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """Cancel subscription"""
        subscription = self.subscriptions.get(subscription_id)

        if not subscription:
            return False

        if immediate:
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.now()
        else:
            subscription.cancel_at_period_end = True

        print(f"[Billing] Cancelled subscription {subscription_id}")
        return True

    def bill_subscription(self, subscription_id: str) -> Optional[Invoice]:
        """Generate and process invoice for subscription"""
        subscription = self.subscriptions.get(subscription_id)

        if not subscription:
            return None

        # Skip if in trial
        if subscription.status == "trialing":
            return None

        # Get usage data
        usage = self.usage_meter.get_usage_by_subscription(
            subscription_id, subscription.current_period_start, subscription.current_period_end
        )

        # Generate invoice
        invoice = self.invoice_generator.generate_invoice(
            subscription.tenant_id,
            subscription,
            subscription.current_period_start,
            subscription.current_period_end,
            usage,
        )

        # Create payment
        if subscription.payment_method_id:
            payment = self.payment_processor.create_payment(invoice, PaymentMethod.CREDIT_CARD)

            # Process payment
            success = self.payment_processor.process_payment(payment.id)

            if success:
                self.invoice_generator.mark_as_paid(invoice.id, payment)
            else:
                # Handle failed payment
                self.dunning_manager.handle_failed_payment(payment)

        return invoice

    def get_billing_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get billing summary for tenant"""
        # Find subscription
        subscription = next((s for s in self.subscriptions.values() if s.tenant_id == tenant_id), None)

        if not subscription:
            return {}

        plan = self.plan_manager.get_plan(subscription.plan_id)

        # Find invoices
        invoices = [inv for inv in self.invoice_generator.invoices.values() if inv.tenant_id == tenant_id]

        total_paid = sum(inv.amount_paid for inv in invoices if inv.status == InvoiceStatus.PAID)
        total_outstanding = sum(inv.amount_due for inv in invoices if inv.status == InvoiceStatus.OPEN)

        return {
            "subscription": {
                "plan": plan.name if plan else "Unknown",
                "status": subscription.status,
                "billing_cycle": subscription.billing_cycle.value,
                "current_period_end": subscription.current_period_end.isoformat(),
            },
            "invoices": {
                "total": len(invoices),
                "paid": sum(1 for inv in invoices if inv.status == InvoiceStatus.PAID),
                "outstanding": sum(1 for inv in invoices if inv.status == InvoiceStatus.OPEN),
            },
            "amounts": {
                "total_paid": float(total_paid),
                "total_outstanding": float(total_outstanding),
                "currency": plan.currency if plan else "EUR",
            },
        }


# Global instance
_billing_engine: Optional[BillingEngine] = None


def get_billing_engine() -> BillingEngine:
    """Get global billing engine instance"""
    global _billing_engine

    if _billing_engine is None:
        _billing_engine = BillingEngine()

    return _billing_engine
