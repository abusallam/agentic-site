"""Stripe service for payment processing."""

import os
from typing import Dict, Optional, Any, List
import logging
import stripe

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling payments via Stripe."""
    
    def __init__(self):
        """Initialize Stripe service."""
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not self.api_key:
            logger.warning("Stripe API key not found, using mock mode")
            self.mock_mode = True
        else:
            stripe.api_key = self.api_key
            self.mock_mode = False
    
    async def create_customer(self, email: str, name: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Create a new Stripe customer."""
        if self.mock_mode:
            logger.info(f"Mock: Creating Stripe customer for {email}")
            return {
                "id": f"cus_mock_{email.replace('@', '_').replace('.', '_')}",
                "email": email,
                "name": name,
                "metadata": metadata or {}
            }
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "metadata": customer.metadata
            }
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    async def create_payment_intent(self, amount: int, currency: str, customer_id: str, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a payment intent for a customer."""
        if self.mock_mode:
            logger.info(f"Mock: Creating payment intent for {amount} {currency}")
            return {
                "id": f"pi_mock_{customer_id}_{amount}",
                "client_secret": f"pi_mock_{customer_id}_{amount}_secret",
                "amount": amount,
                "currency": currency,
                "status": "requires_payment_method"
            }
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
                automatic_payment_methods={"enabled": True}
            )
            logger.info(f"Created payment intent: {intent.id}")
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status
            }
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            return None
    
    async def create_subscription(self, customer_id: str, price_id: str, metadata: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Create a subscription for a customer."""
        if self.mock_mode:
            logger.info(f"Mock: Creating subscription for customer {customer_id}")
            return {
                "id": f"sub_mock_{customer_id}",
                "customer": customer_id,
                "status": "active",
                "current_period_start": 1640995200,  # 2022-01-01
                "current_period_end": 1672531200,    # 2023-01-01
                "metadata": metadata or {}
            }
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {}
            )
            logger.info(f"Created subscription: {subscription.id}")
            return {
                "id": subscription.id,
                "customer": subscription.customer,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "metadata": subscription.metadata
            }
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None
    
    async def get_customer_payments(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get payment history for a customer."""
        if self.mock_mode:
            logger.info(f"Mock: Getting payments for customer {customer_id}")
            return [
                {
                    "id": f"pi_mock_{customer_id}_1",
                    "amount": 5000,
                    "currency": "usd",
                    "status": "succeeded",
                    "created": 1640995200
                }
            ]
        
        try:
            charges = stripe.Charge.list(customer=customer_id, limit=100)
            payments = []
            for charge in charges.data:
                payments.append({
                    "id": charge.id,
                    "amount": charge.amount,
                    "currency": charge.currency,
                    "status": charge.status,
                    "created": charge.created,
                    "description": charge.description
                })
            logger.info(f"Retrieved {len(payments)} payments for customer {customer_id}")
            return payments
        except Exception as e:
            logger.error(f"Failed to get customer payments: {e}")
            return []
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a customer subscription."""
        if self.mock_mode:
            logger.info(f"Mock: Canceling subscription {subscription_id}")
            return True
        
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"Canceled subscription: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    async def create_product_price(self, product_name: str, amount: int, currency: str, interval: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a product and price for services."""
        if self.mock_mode:
            logger.info(f"Mock: Creating product {product_name} with price {amount} {currency}")
            return {
                "product_id": f"prod_mock_{product_name.lower().replace(' ', '_')}",
                "price_id": f"price_mock_{product_name.lower().replace(' ', '_')}",
                "amount": amount,
                "currency": currency,
                "interval": interval
            }
        
        try:
            # Create product
            product = stripe.Product.create(name=product_name)
            
            # Create price
            price_data = {
                "product": product.id,
                "unit_amount": amount,
                "currency": currency,
            }
            
            if interval:
                price_data["recurring"] = {"interval": interval}
            
            price = stripe.Price.create(**price_data)
            
            logger.info(f"Created product {product.id} with price {price.id}")
            return {
                "product_id": product.id,
                "price_id": price.id,
                "amount": amount,
                "currency": currency,
                "interval": interval
            }
        except Exception as e:
            logger.error(f"Failed to create product and price: {e}")
            return None