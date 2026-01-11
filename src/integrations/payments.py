"""
Payment Gateway Integration

Provides integrations with major payment providers:
- Stripe
- PayPal
- Square
- Braintree
- Adyen
- Mollie (EU)
- Klarna
- Generic payment processing
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import hashlib


class PaymentProvider(str, Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    BRAINTREE = "braintree"
    ADYEN = "adyen"
    MOLLIE = "mollie"
    KLARNA = "klarna"
    AUTHORIZE_NET = "authorize_net"
    WORLDPAY = "worldpay"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    SEPA_DEBIT = "sepa_debit"
    PAYPAL_ACCOUNT = "paypal_account"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    KLARNA = "klarna"
    SOFORT = "sofort"
    IDEAL = "ideal"  # Netherlands
    GIROPAY = "giropay"  # Germany


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Currency(str, Enum):
    """Supported currencies"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
    JPY = "JPY"
    CNY = "CNY"


@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration"""
    id: str
    provider: PaymentProvider
    name: str
    api_key: str
    secret_key: str
    publishable_key: Optional[str] = None
    merchant_id: Optional[str] = None
    environment: str = "production"  # production, sandbox
    webhook_secret: Optional[str] = None
    enabled: bool = True
    supported_currencies: List[Currency] = field(default_factory=lambda: [Currency.EUR, Currency.USD])
    supported_methods: List[PaymentMethod] = field(default_factory=lambda: [PaymentMethod.CARD])


@dataclass
class PaymentCustomer:
    """Payment customer"""
    id: Optional[str] = None
    email: str = ""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentIntent:
    """Payment intent/transaction"""
    id: str
    provider: PaymentProvider
    amount: float
    currency: Currency
    customer: Optional[PaymentCustomer] = None
    payment_method: Optional[PaymentMethod] = None
    status: PaymentStatus = PaymentStatus.PENDING
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    provider_transaction_id: Optional[str] = None
    fee: float = 0.0
    net_amount: float = 0.0


@dataclass
class Refund:
    """Payment refund"""
    id: str
    payment_id: str
    amount: float
    currency: Currency
    reason: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    provider_refund_id: Optional[str] = None


@dataclass
class Subscription:
    """Recurring subscription"""
    id: str
    customer_id: str
    amount: float
    currency: Currency
    interval: str  # day, week, month, year
    interval_count: int = 1
    status: str = "active"  # active, canceled, past_due
    current_period_start: datetime = field(default_factory=datetime.now)
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class StripeConnector:
    """Stripe payment connector"""

    def __init__(self, config: PaymentGatewayConfig):
        self.config = config
        self.api_key = config.secret_key

    def create_payment_intent(
        self,
        amount: float,
        currency: Currency,
        customer: Optional[PaymentCustomer] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Create Stripe payment intent"""
        # In production, use stripe library
        # import stripe
        # stripe.api_key = self.api_key
        # intent = stripe.PaymentIntent.create(
        #     amount=int(amount * 100),  # Stripe uses cents
        #     currency=currency.value.lower(),
        #     customer=customer.id if customer else None,
        #     metadata=metadata
        # )

        # Simulated response
        intent_id = str(uuid.uuid4())
        stripe_id = f"pi_{uuid.uuid4().hex[:24]}"

        payment = PaymentIntent(
            id=intent_id,
            provider=PaymentProvider.STRIPE,
            amount=amount,
            currency=currency,
            customer=customer,
            status=PaymentStatus.PROCESSING,
            metadata=metadata or {},
            provider_transaction_id=stripe_id,
            fee=amount * 0.029 + 0.30,  # Stripe fee: 2.9% + $0.30
            net_amount=amount - (amount * 0.029 + 0.30)
        )

        print(f"[Stripe] Created payment intent: {stripe_id} for {amount} {currency.value}")
        return payment

    def confirm_payment(self, payment_id: str) -> bool:
        """Confirm payment"""
        # stripe.PaymentIntent.confirm(payment_id)

        print(f"[Stripe] Confirmed payment: {payment_id}")
        return True

    def create_refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Refund:
        """Create refund"""
        # stripe.Refund.create(
        #     payment_intent=payment_id,
        #     amount=int(amount * 100) if amount else None,
        #     reason=reason
        # )

        refund_id = str(uuid.uuid4())
        stripe_refund_id = f"re_{uuid.uuid4().hex[:24]}"

        refund = Refund(
            id=refund_id,
            payment_id=payment_id,
            amount=amount or 0.0,
            currency=Currency.EUR,
            reason=reason,
            status=PaymentStatus.PROCESSING,
            provider_refund_id=stripe_refund_id
        )

        print(f"[Stripe] Created refund: {stripe_refund_id}")
        return refund

    def create_customer(self, customer: PaymentCustomer) -> str:
        """Create Stripe customer"""
        # stripe_customer = stripe.Customer.create(
        #     email=customer.email,
        #     name=customer.name,
        #     metadata=customer.metadata
        # )

        customer_id = f"cus_{uuid.uuid4().hex[:14]}"
        customer.id = customer_id

        print(f"[Stripe] Created customer: {customer_id}")
        return customer_id

    def create_subscription(self, subscription: Subscription) -> str:
        """Create subscription"""
        # stripe.Subscription.create(
        #     customer=subscription.customer_id,
        #     items=[{'price': price_id}],
        #     metadata=subscription.metadata
        # )

        sub_id = f"sub_{uuid.uuid4().hex[:14]}"
        print(f"[Stripe] Created subscription: {sub_id}")
        return sub_id


class PayPalConnector:
    """PayPal payment connector"""

    def __init__(self, config: PaymentGatewayConfig):
        self.config = config
        self.client_id = config.api_key
        self.secret = config.secret_key
        self.base_url = "https://api-m.paypal.com" if config.environment == "production" else "https://api-m.sandbox.paypal.com"

    def create_order(
        self,
        amount: float,
        currency: Currency,
        description: Optional[str] = None
    ) -> PaymentIntent:
        """Create PayPal order"""
        # In production, use paypalrestsdk or requests
        # POST /v2/checkout/orders

        order_id = str(uuid.uuid4())
        paypal_order_id = uuid.uuid4().hex[:17].upper()

        payment = PaymentIntent(
            id=order_id,
            provider=PaymentProvider.PAYPAL,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            description=description,
            provider_transaction_id=paypal_order_id,
            fee=amount * 0.0349 + 0.49,  # PayPal fee: 3.49% + $0.49
            net_amount=amount - (amount * 0.0349 + 0.49)
        )

        print(f"[PayPal] Created order: {paypal_order_id} for {amount} {currency.value}")
        return payment

    def capture_order(self, order_id: str) -> bool:
        """Capture PayPal order"""
        # POST /v2/checkout/orders/{order_id}/capture

        print(f"[PayPal] Captured order: {order_id}")
        return True

    def create_refund(
        self,
        capture_id: str,
        amount: Optional[float] = None
    ) -> Refund:
        """Create PayPal refund"""
        # POST /v2/payments/captures/{capture_id}/refund

        refund_id = str(uuid.uuid4())
        paypal_refund_id = uuid.uuid4().hex[:17].upper()

        refund = Refund(
            id=refund_id,
            payment_id=capture_id,
            amount=amount or 0.0,
            currency=Currency.EUR,
            status=PaymentStatus.PROCESSING,
            provider_refund_id=paypal_refund_id
        )

        print(f"[PayPal] Created refund: {paypal_refund_id}")
        return refund


class SquareConnector:
    """Square payment connector"""

    def __init__(self, config: PaymentGatewayConfig):
        self.config = config
        self.access_token = config.api_key
        self.base_url = "https://connect.squareup.com" if config.environment == "production" else "https://connect.squareupsandbox.com"

    def create_payment(
        self,
        amount: float,
        currency: Currency,
        source_id: str,
        customer: Optional[PaymentCustomer] = None
    ) -> PaymentIntent:
        """Create Square payment"""
        # In production, use square SDK
        # from square.client import Client
        # POST /v2/payments

        payment_id = str(uuid.uuid4())
        square_payment_id = uuid.uuid4().hex

        payment = PaymentIntent(
            id=payment_id,
            provider=PaymentProvider.SQUARE,
            amount=amount,
            currency=currency,
            customer=customer,
            status=PaymentStatus.PROCESSING,
            provider_transaction_id=square_payment_id,
            fee=amount * 0.029 + 0.30,  # Square fee: 2.9% + $0.30
            net_amount=amount - (amount * 0.029 + 0.30)
        )

        print(f"[Square] Created payment: {square_payment_id} for {amount} {currency.value}")
        return payment

    def create_refund(
        self,
        payment_id: str,
        amount: float,
        currency: Currency
    ) -> Refund:
        """Create Square refund"""
        # POST /v2/refunds

        refund_id = str(uuid.uuid4())
        square_refund_id = uuid.uuid4().hex

        refund = Refund(
            id=refund_id,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PROCESSING,
            provider_refund_id=square_refund_id
        )

        print(f"[Square] Created refund: {square_refund_id}")
        return refund


class PaymentGateway:
    """Main payment gateway manager"""

    def __init__(self, database=None):
        self.database = database
        self.configs: Dict[str, PaymentGatewayConfig] = {}
        self.connectors: Dict[str, Any] = {}
        self.payments: List[PaymentIntent] = []
        self.refunds: List[Refund] = []

    def register_gateway(self, config: PaymentGatewayConfig) -> str:
        """Register payment gateway"""
        self.configs[config.id] = config
        return config.id

    def get_connector(self, gateway_id: str) -> Optional[Any]:
        """Get or create payment connector"""
        if gateway_id not in self.configs:
            return None

        if gateway_id in self.connectors:
            return self.connectors[gateway_id]

        config = self.configs[gateway_id]

        # Create appropriate connector
        if config.provider == PaymentProvider.STRIPE:
            connector = StripeConnector(config)
        elif config.provider == PaymentProvider.PAYPAL:
            connector = PayPalConnector(config)
        elif config.provider == PaymentProvider.SQUARE:
            connector = SquareConnector(config)
        else:
            return None

        self.connectors[gateway_id] = connector
        return connector

    def create_payment(
        self,
        gateway_id: str,
        amount: float,
        currency: Currency,
        customer: Optional[PaymentCustomer] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PaymentIntent]:
        """Create payment"""
        connector = self.get_connector(gateway_id)
        if not connector:
            return None

        try:
            if isinstance(connector, StripeConnector):
                payment = connector.create_payment_intent(
                    amount, currency, customer, metadata
                )
            elif isinstance(connector, PayPalConnector):
                payment = connector.create_order(amount, currency, description)
            elif isinstance(connector, SquareConnector):
                # Square requires source_id (card token)
                payment = connector.create_payment(
                    amount, currency, "simulated_source_id", customer
                )
            else:
                return None

            self.payments.append(payment)
            return payment

        except Exception as e:
            print(f"[Payment] Error creating payment: {e}")
            return None

    def confirm_payment(self, payment_id: str) -> bool:
        """Confirm/capture payment"""
        # Find payment
        payment = None
        for p in self.payments:
            if p.id == payment_id:
                payment = p
                break

        if not payment:
            return False

        # Get connector
        connector = None
        for gw_id, config in self.configs.items():
            if config.provider == payment.provider:
                connector = self.get_connector(gw_id)
                break

        if not connector:
            return False

        try:
            if isinstance(connector, StripeConnector):
                success = connector.confirm_payment(payment.provider_transaction_id)
            elif isinstance(connector, PayPalConnector):
                success = connector.capture_order(payment.provider_transaction_id)
            else:
                success = True  # Square auto-captures

            if success:
                payment.status = PaymentStatus.SUCCEEDED

            return success

        except Exception as e:
            print(f"[Payment] Error confirming payment: {e}")
            payment.status = PaymentStatus.FAILED
            return False

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Optional[Refund]:
        """Refund payment"""
        # Find payment
        payment = None
        for p in self.payments:
            if p.id == payment_id:
                payment = p
                break

        if not payment or payment.status != PaymentStatus.SUCCEEDED:
            return None

        # Get connector
        connector = None
        for gw_id, config in self.configs.items():
            if config.provider == payment.provider:
                connector = self.get_connector(gw_id)
                break

        if not connector:
            return None

        try:
            refund_amount = amount or payment.amount

            if isinstance(connector, StripeConnector):
                refund = connector.create_refund(
                    payment.provider_transaction_id,
                    refund_amount,
                    reason
                )
            elif isinstance(connector, PayPalConnector):
                refund = connector.create_refund(
                    payment.provider_transaction_id,
                    refund_amount
                )
            elif isinstance(connector, SquareConnector):
                refund = connector.create_refund(
                    payment.provider_transaction_id,
                    refund_amount,
                    payment.currency
                )
            else:
                return None

            self.refunds.append(refund)

            # Update payment status
            if refund_amount >= payment.amount:
                payment.status = PaymentStatus.REFUNDED
            else:
                payment.status = PaymentStatus.PARTIALLY_REFUNDED

            return refund

        except Exception as e:
            print(f"[Payment] Error creating refund: {e}")
            return None

    def get_payment(self, payment_id: str) -> Optional[PaymentIntent]:
        """Get payment by ID"""
        for payment in self.payments:
            if payment.id == payment_id:
                return payment
        return None

    def get_payments(
        self,
        customer_email: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        limit: int = 50
    ) -> List[PaymentIntent]:
        """Get payments with filters"""
        payments = self.payments

        if customer_email:
            payments = [
                p for p in payments
                if p.customer and p.customer.email == customer_email
            ]

        if status:
            payments = [p for p in payments if p.status == status]

        # Return most recent
        return sorted(payments, key=lambda x: x.created_at, reverse=True)[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get payment statistics"""
        total_payments = len(self.payments)
        successful_payments = len([p for p in self.payments if p.status == PaymentStatus.SUCCEEDED])
        total_revenue = sum(p.amount for p in self.payments if p.status == PaymentStatus.SUCCEEDED)
        total_fees = sum(p.fee for p in self.payments if p.status == PaymentStatus.SUCCEEDED)
        total_refunded = sum(r.amount for r in self.refunds)

        return {
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'failed_payments': len([p for p in self.payments if p.status == PaymentStatus.FAILED]),
            'success_rate': (successful_payments / total_payments * 100) if total_payments > 0 else 0,
            'total_revenue': total_revenue,
            'total_fees': total_fees,
            'net_revenue': total_revenue - total_fees - total_refunded,
            'total_refunded': total_refunded,
            'refund_count': len(self.refunds),
            'active_gateways': len([c for c in self.configs.values() if c.enabled])
        }


# Global instance
_payment_gateway: Optional[PaymentGateway] = None


def get_payment_gateway(database=None) -> PaymentGateway:
    """Get global payment gateway instance"""
    global _payment_gateway

    if _payment_gateway is None:
        _payment_gateway = PaymentGateway(database)

    return _payment_gateway


def configure_payment_gateway(database):
    """Configure payment gateway"""
    global _payment_gateway
    _payment_gateway = PaymentGateway(database)
