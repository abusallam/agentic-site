"""Livekit service for real-time communication and live agent handoff."""

import os
from typing import Dict, Optional, Any, List
import logging

try:
    from livekit import api
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    api = None

logger = logging.getLogger(__name__)


class LivekitService:
    """Service for managing real-time communication with Livekit."""
    
    def __init__(self):
        """Initialize Livekit service."""
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.ws_url = os.getenv("LIVEKIT_WS_URL", "wss://localhost:7880")
        
        if not self.api_key or not self.api_secret or not LIVEKIT_AVAILABLE:
            logger.warning("Livekit credentials not found or Livekit not available, using mock mode")
            self.client = None
        else:
            self.client = api.LiveKitAPI(
                url=self.ws_url,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
    
    async def create_room(self, room_name: str, customer_id: str) -> Optional[Dict[str, Any]]:
        """Create a new room for customer-agent communication."""
        if not self.client:
            logger.info(f"Mock: Creating room {room_name} for customer {customer_id}")
            return {
                "room_name": room_name,
                "room_id": f"mock-room-{customer_id}",
                "customer_id": customer_id,
                "status": "created"
            }
        
        try:
            room = await self.client.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    metadata=f"customer_id:{customer_id}"
                )
            )
            logger.info(f"Created room {room_name} for customer {customer_id}")
            return {
                "room_name": room.name,
                "room_id": room.sid,
                "customer_id": customer_id,
                "status": "created"
            }
        except Exception as e:
            logger.error(f"Failed to create room: {e}")
            return None
    
    async def generate_access_token(self, room_name: str, participant_name: str, is_agent: bool = False) -> Optional[str]:
        """Generate access token for room participant."""
        if not self.client:
            logger.info(f"Mock: Generating token for {participant_name} in room {room_name}")
            return f"mock-token-{participant_name}"
        
        try:
            if not LIVEKIT_AVAILABLE:
                logger.info(f"Mock: Generating token for {participant_name} in room {room_name}")
                return f"mock-token-{participant_name}"
            
            from livekit import AccessToken, VideoGrants
            
            token = AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_name)
            token.with_name(participant_name)
            
            grants = VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True if is_agent else False
            )
            token.with_grants(grants)
            
            access_token = token.to_jwt()
            logger.info(f"Generated access token for {participant_name}")
            return access_token
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            return None
    
    async def invite_live_agent(self, room_name: str, agent_email: str) -> bool:
        """Invite a live agent to join the room."""
        if not self.client:
            logger.info(f"Mock: Inviting agent {agent_email} to room {room_name}")
            return True
        
        try:
            # In a real implementation, this would send a notification to the agent
            # For now, we'll just log the invitation
            logger.info(f"Invited live agent {agent_email} to room {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to invite live agent: {e}")
            return False
    
    async def get_room_participants(self, room_name: str) -> List[Dict[str, Any]]:
        """Get list of participants in a room."""
        if not self.client:
            logger.info(f"Mock: Getting participants for room {room_name}")
            return [
                {"identity": "customer", "name": "Customer", "joined_at": "2024-01-01T00:00:00Z"},
                {"identity": "agent", "name": "Live Agent", "joined_at": "2024-01-01T00:05:00Z"}
            ]
        
        try:
            participants = await self.client.room.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )
            
            result = []
            for participant in participants.participants:
                result.append({
                    "identity": participant.identity,
                    "name": participant.name,
                    "joined_at": participant.joined_at,
                    "is_publisher": len(participant.tracks) > 0
                })
            
            logger.info(f"Retrieved {len(result)} participants from room {room_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to get room participants: {e}")
            return []
    
    async def end_room_session(self, room_name: str) -> bool:
        """End a room session and disconnect all participants."""
        if not self.client:
            logger.info(f"Mock: Ending room session {room_name}")
            return True
        
        try:
            await self.client.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            logger.info(f"Ended room session: {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to end room session: {e}")
            return False
    
    async def monitor_room_events(self, room_name: str) -> Dict[str, Any]:
        """Monitor room events for AI agent listening."""
        if not self.client:
            logger.info(f"Mock: Monitoring events for room {room_name}")
            return {
                "room_name": room_name,
                "events": ["participant_joined", "message_received"],
                "status": "monitoring"
            }
        
        try:
            # In a real implementation, this would set up event listeners
            # For now, we'll return a mock monitoring status
            logger.info(f"Started monitoring room events: {room_name}")
            return {
                "room_name": room_name,
                "status": "monitoring",
                "events_tracked": ["participant_joined", "participant_left", "data_received"]
            }
        except Exception as e:
            logger.error(f"Failed to monitor room events: {e}")
            return {"status": "error", "error": str(e)}