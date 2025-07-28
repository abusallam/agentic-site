"""Authentication service for customer management."""

import os
from typing import Dict, Optional, Any
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling customer authentication."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        self.key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found, using mock mode")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
    
    async def authenticate_customer(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate customer with email and password."""
        if not self.client:
            logger.info(f"Mock: Authenticating customer {email}")
            return {
                "user": {"id": "mock-user-id", "email": email},
                "session": {"access_token": "mock-token"}
            }
        
        try:
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            logger.info(f"Authenticated customer: {email}")
            return {
                "user": result.user,
                "session": result.session
            }
        except Exception as e:
            logger.error(f"Authentication failed for {email}: {e}")
            return None
    
    async def register_customer(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Register a new customer."""
        if not self.client:
            logger.info(f"Mock: Registering customer {email}")
            return {
                "user": {"id": "mock-user-id", "email": email},
                "session": {"access_token": "mock-token"}
            }
        
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": metadata} if metadata else None
            })
            logger.info(f"Registered customer: {email}")
            return {
                "user": result.user,
                "session": result.session
            }
        except Exception as e:
            logger.error(f"Registration failed for {email}: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify authentication token."""
        if not self.client:
            logger.info("Mock: Verifying token")
            return {"user": {"id": "mock-user-id", "email": "mock@example.com"}}
        
        try:
            result = self.client.auth.get_user(token)
            return {"user": result.user}
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email."""
        if not self.client:
            logger.info(f"Mock: Sending password reset to {email}")
            return True
        
        try:
            self.client.auth.reset_password_email(email)
            logger.info(f"Password reset sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Password reset failed for {email}: {e}")
            return False
    
    async def update_customer_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update customer profile information."""
        if not self.client:
            logger.info(f"Mock: Updating profile for user {user_id}")
            return True
        
        try:
            result = self.client.auth.update_user({
                "data": updates
            })
            logger.info(f"Updated profile for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Profile update failed for {user_id}: {e}")
            return False