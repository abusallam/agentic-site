"""
Stripe Service - Payment processing integration
Handles payment methods, invoices, and transactions
"""

import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class StripeService:
    """Service for Stripe payment processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        # Initialize Stripe (mock for development)
        try:
            import stripe
            stripe.api_key = self.api_key
            self.stripe = stripe
        except ImportError:
            logger.warning("Stripe not installed, using mock implementation")
            self.stripe = MockStripe()
    
    async def get_or_create_customer(self, customer_id: str) -> Any:
        """Get or create Stripe customer"""
        try:
            # Try to find existing customer
            customers = self.stripe.Customer.list(
                metadata={'customer_id': customer_id},
                limit=1
            )
            
            if customers.data:
                return customers.data[0]
            
            # Create new customer
            customer = self.stripe.Customer.create(
                metadata={'customer_id': customer_id}
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer
            
        except Exception as e:
            logger.error(f"Error with Stripe customer: {e}")
            raise
    
    async def setup_payment_method(self, stripe_customer_id: str, payment_method_data: Dict[str, Any]) -> Any:
        """Setup payment method for customer"""
        try:
            # Create payment method
            payment_method = self.stripe.PaymentMethod.create(
                type='card',
                card=payment_method_data.get('card', {}),
            )
            
            # Attach to customer
            payment_method.attach(customer=stripe_customer_id)
            
            logger.info(f"Setup payment method: {payment_method.id}")
            return payment_method
            
        except Exception as e:
            logger.error(f"Error setting up payment method: {e}")
            raise
    
    async def process_payment(self, amount: int, currency: str, customer_id: str, 
                            payment_method_id: str, description: str) -> Any:
        """Process payment using Stripe"""
        try:
            # Create payment intent
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency.lower(),
                customer=customer_id,
                payment_method=payment_method_id,
                description=description,
                confirm=True,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )
            
            logger.info(f"Processed payment: {payment_intent.id}")
            return payment_intent
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise
    
    async def create_invoice(self, customer_id: str, line_items: list, 
                           metadata: Dict[str, Any] = None) -> Any:
        """Create Stripe invoice"""
        try:
            # Create invoice
            invoice = self.stripe.Invoice.create(
                customer=customer_id,
                metadata=metadata or {},
                auto_advance=True
            )
            
            # Add line items
            for item in line_items:
                self.stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=invoice.id,
                    amount=int(item['amount'] * 100),  # Convert to cents
                    currency='sar',
                    description=item['description']
                )
            
            # Finalize invoice
            invoice.finalize_invoice()
            
            logger.info(f"Created Stripe invoice: {invoice.id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            raise


class MockStripe:
    """Mock Stripe implementation for development"""
    
    class Customer:
        @staticmethod
        def list(**kwargs):
            return type('MockList', (), {'data': []})()
        
        @staticmethod
        def create(**kwargs):
            return type('MockCustomer', (), {
                'id': 'cus_mock_123',
                'metadata': kwargs.get('metadata', {})
            })()
    
    class PaymentMethod:
        @staticmethod
        def create(**kwargs):
            return type('MockPaymentMethod', (), {
                'id': 'pm_mock_123',
                'type': 'card',
                'card': type('MockCard', (), {
                    'last4': '4242',
                    'brand': 'visa'
                })(),
                'attach': lambda customer: None
            })()
    
    class PaymentIntent:
        @staticmethod
        def create(**kwargs):
            return type('MockPaymentIntent', (), {
                'id': 'pi_mock_123',
                'status': 'succeeded',
                'amount': kwargs.get('amount', 0),
                'currency': kwargs.get('currency', 'sar')
            })()
    
    class Invoice:
        @staticmethod
        def create(**kwargs):
            return type('MockInvoice', (), {
                'id': 'in_mock_123',
                'finalize_invoice': lambda: None
            })()
    
    class InvoiceItem:
        @staticmethod
        def create(**kwargs):
            return type('MockInvoiceItem', (), {
                'id': 'ii_mock_123'
            })()