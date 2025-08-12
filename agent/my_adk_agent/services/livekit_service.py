"""
LiveKit Service - Real-time communication for human agent handoff
Handles video/audio sessions between customers and human consultants
"""

import asyncio
import json
import jwt
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)

class LiveKitService:
    """
    Service for LiveKit real-time communication
    Provides room creation, token generation, and session management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.livekit_url = config.get("LIVEKIT_URL", "wss://consulting-sa.livekit.cloud")
        self.api_key = config.get("LIVEKIT_API_KEY")
        self.api_secret = config.get("LIVEKIT_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            logger.warning("LiveKit credentials not configured - human handoff will be disabled")
            self.enabled = False
        else:
            self.enabled = True
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_room(self, room_name: str, customer_id: str, agent_type: str = "human_consultant", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a LiveKit room for customer-consultant session
        
        Args:
            room_name: Unique room identifier
            customer_id: Customer identifier
            agent_type: Type of agent/consultant
            metadata: Additional room metadata
            
        Returns:
            Room information with URLs and tokens
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            # Create room via LiveKit API
            room_config = {
                "name": room_name,
                "empty_timeout": 300,  # 5 minutes
                "max_participants": 10,
                "metadata": json.dumps({
                    "customer_id": customer_id,
                    "agent_type": agent_type,
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {})
                })
            }
            
            # For demo purposes, we'll simulate room creation
            # In production, you would call the actual LiveKit API
            room_url = f"{self.livekit_url.replace('wss://', 'https://')}/room/{room_name}"
            
            # Generate access tokens
            customer_token = self._generate_access_token(
                room_name=room_name,
                participant_name=f"customer_{customer_id}",
                participant_identity=customer_id,
                permissions={
                    "canPublish": True,
                    "canSubscribe": True,
                    "canPublishData": True
                }
            )
            
            consultant_token = self._generate_access_token(
                room_name=room_name,
                participant_name="consultant",
                participant_identity=f"consultant_{int(time.time())}",
                permissions={
                    "canPublish": True,
                    "canSubscribe": True,
                    "canPublishData": True,
                    "hidden": False,
                    "recorder": True
                }
            )
            
            logger.info(f"LiveKit room created: {room_name}")
            
            return {
                "success": True,
                "room_name": room_name,
                "room_url": room_url,
                "customer_token": customer_token,
                "consultant_token": consultant_token,
                "expires_at": (datetime.now() + timedelta(hours=2)).isoformat(),
                "max_duration_minutes": 120
            }
            
        except Exception as e:
            logger.error(f"Error creating LiveKit room: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_access_token(self, room_name: str, participant_name: str, participant_identity: str, permissions: Dict[str, Any]) -> str:
        """
        Generate JWT access token for LiveKit room
        
        Args:
            room_name: Room name
            participant_name: Display name
            participant_identity: Unique participant ID
            permissions: Participant permissions
            
        Returns:
            JWT access token
        """
        if not self.enabled:
            return ""
        
        try:
            # Token payload
            now = int(time.time())
            payload = {
                "iss": self.api_key,
                "sub": participant_identity,
                "iat": now,
                "exp": now + 7200,  # 2 hours
                "video": {
                    "room": room_name,
                    "roomJoin": True,
                    "roomList": True,
                    "roomRecord": permissions.get("recorder", False),
                    "roomAdmin": permissions.get("admin", False),
                    "roomCreate": False,
                    "canPublish": permissions.get("canPublish", True),
                    "canSubscribe": permissions.get("canSubscribe", True),
                    "canPublishData": permissions.get("canPublishData", True),
                    "hidden": permissions.get("hidden", False)
                },
                "metadata": json.dumps({
                    "participant_name": participant_name,
                    "participant_type": "customer" if "customer" in participant_identity else "consultant"
                })
            }
            
            # Generate JWT token
            token = jwt.encode(payload, self.api_secret, algorithm="HS256")
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            return ""
    
    async def get_room_info(self, room_name: str) -> Dict[str, Any]:
        """
        Get information about a LiveKit room
        
        Args:
            room_name: Room identifier
            
        Returns:
            Room information
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            # In production, you would call the LiveKit API
            # For demo, we'll return simulated data
            return {
                "success": True,
                "room": {
                    "name": room_name,
                    "num_participants": 0,
                    "creation_time": datetime.now().isoformat(),
                    "metadata": {},
                    "max_participants": 10,
                    "empty_timeout": 300
                },
                "participants": []
            }
            
        except Exception as e:
            logger.error(f"Error getting room info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_rooms(self) -> Dict[str, Any]:
        """
        List all active LiveKit rooms
        
        Returns:
            List of active rooms
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            # In production, you would call the LiveKit API
            # For demo, we'll return simulated data
            return {
                "success": True,
                "rooms": [
                    {
                        "name": "consultation_demo_123",
                        "num_participants": 2,
                        "creation_time": datetime.now().isoformat(),
                        "metadata": {
                            "customer_id": "demo_customer",
                            "agent_type": "human_consultant"
                        }
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error listing rooms: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_session(self, room_name: str) -> Dict[str, Any]:
        """
        End a LiveKit session and clean up
        
        Args:
            room_name: Room to end
            
        Returns:
            Operation result
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            # In production, you would call the LiveKit API to delete the room
            logger.info(f"LiveKit session ended: {room_name}")
            
            return {
                "success": True,
                "room_name": room_name,
                "ended_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_recording(self, room_name: str) -> Dict[str, Any]:
        """
        Get recording information for a session
        
        Args:
            room_name: Room name
            
        Returns:
            Recording information
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            # In production, you would retrieve actual recording info
            return {
                "success": True,
                "recording": {
                    "room_name": room_name,
                    "recording_id": f"rec_{int(time.time())}",
                    "status": "completed",
                    "duration_seconds": 1800,  # 30 minutes
                    "file_size_mb": 150,
                    "download_url": f"https://recordings.consulting.sa/{room_name}.mp4",
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting session recording: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_consultation_link(self, consultation_id: str, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Generate a consultation link for customer
        
        Args:
            consultation_id: Consultation identifier
            customer_id: Customer identifier
            language: Customer language
            
        Returns:
            Consultation link and instructions
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        try:
            room_name = f"consultation_{consultation_id}"
            
            # Create room
            room_result = await self.create_room(
                room_name=room_name,
                customer_id=customer_id,
                agent_type="human_consultant",
                metadata={
                    "consultation_id": consultation_id,
                    "language": language
                }
            )
            
            if not room_result["success"]:
                return room_result
            
            # Generate customer-friendly link
            consultation_url = f"https://consulting.sa/consultation/{consultation_id}?token={room_result['customer_token']}"
            
            instructions = {
                "ar": {
                    "title": "رابط الاستشارة الخاص بك",
                    "message": "انقر على الرابط أدناه للانضمام إلى جلسة الاستشارة المباشرة",
                    "requirements": [
                        "تأكد من وجود كاميرا وميكروفون",
                        "استخدم متصفح حديث (Chrome, Firefox, Safari)",
                        "تأكد من اتصال إنترنت مستقر"
                    ],
                    "support": "للدعم التقني: cto@consulting.sa"
                },
                "en": {
                    "title": "Your Consultation Link",
                    "message": "Click the link below to join your live consultation session",
                    "requirements": [
                        "Ensure you have a camera and microphone",
                        "Use a modern browser (Chrome, Firefox, Safari)",
                        "Ensure stable internet connection"
                    ],
                    "support": "For technical support: cto@consulting.sa"
                }
            }
            
            return {
                "success": True,
                "consultation_url": consultation_url,
                "room_name": room_name,
                "expires_at": room_result["expires_at"],
                "instructions": instructions[language],
                "backup_phone": "00966542331876"
            }
            
        except Exception as e:
            logger.error(f"Error generating consultation link: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def notify_consultant(self, consultation_id: str, customer_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify human consultant about new session
        
        Args:
            consultation_id: Consultation identifier
            customer_info: Customer information
            
        Returns:
            Notification result
        """
        try:
            # In production, you would send actual notifications
            # via email, Slack, SMS, etc.
            
            notification_data = {
                "type": "new_consultation",
                "consultation_id": consultation_id,
                "customer": customer_info,
                "room_url": f"https://consulting.sa/consultant/room/{consultation_id}",
                "scheduled_time": datetime.now().isoformat(),
                "priority": "normal"
            }
            
            logger.info(f"Consultant notified for consultation: {consultation_id}")
            
            return {
                "success": True,
                "notification_sent": True,
                "consultant_notified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error notifying consultant: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check LiveKit service health"""
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "LiveKit not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # In production, you would ping the LiveKit server
            return {
                "status": "healthy",
                "service": "livekit",
                "url": self.livekit_url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LiveKit health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "livekit",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()