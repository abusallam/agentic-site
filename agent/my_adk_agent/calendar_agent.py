"""Calendar Agent for scheduling and appointment management."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.adk.agents.base_agent import BaseAgent

from .services import (
    SupabaseService,
    LivekitService,
)

logger = logging.getLogger(__name__)


class CalendarAgent(BaseAgent):
    """ADK Agent specialized in calendar management, scheduling, and appointments."""
    
    def __init__(self):
        """Initialize the calendar agent."""
        super().__init__(
            name="calendar_agent",
            description="ADK Agent for managing appointments, scheduling meetings, and calendar operations"
        )
        
        # Initialize services
        object.__setattr__(self, 'supabase_service', SupabaseService())
        object.__setattr__(self, 'livekit_service', LivekitService())
        
        logger.info("CalendarAgent initialized")
    
    async def schedule_appointment(self, customer_email: str, appointment_type: str, 
                                 preferred_date: str, preferred_time: str, 
                                 duration_minutes: int = 60) -> Dict[str, Any]:
        """Schedule an appointment for a customer."""
        try:
            logger.info(f"Scheduling {appointment_type} appointment for {customer_email}")
            
            # Get customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Parse date and time
            appointment_datetime = self._parse_datetime(preferred_date, preferred_time)
            if not appointment_datetime:
                return {"status": "error", "error": "Invalid date/time format"}
            
            # Check availability
            is_available = await self._check_availability(appointment_datetime, duration_minutes)
            if not is_available:
                # Suggest alternative times
                alternatives = await self._suggest_alternative_times(appointment_datetime, duration_minutes)
                return {
                    "status": "conflict",
                    "message": "Requested time slot is not available",
                    "alternatives": alternatives
                }
            
            # Create appointment record
            appointment_data = {
                "customer_id": customer["id"],
                "appointment_type": appointment_type,
                "scheduled_at": appointment_datetime.isoformat(),
                "duration_minutes": duration_minutes,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            # Store in database (we'll need to create appointments table)
            appointment = await self._create_appointment_record(appointment_data)
            
            # Create calendar event
            calendar_event = await self._create_calendar_event(appointment_data)
            
            # Send confirmation
            confirmation = await self._send_appointment_confirmation(customer_email, appointment_data)
            
            return {
                "status": "success",
                "appointment_id": appointment["id"] if appointment else None,
                "scheduled_at": appointment_datetime.isoformat(),
                "duration_minutes": duration_minutes,
                "calendar_event_id": calendar_event.get("id") if calendar_event else None,
                "confirmation_sent": confirmation
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule appointment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def reschedule_appointment(self, appointment_id: str, new_date: str, 
                                   new_time: str) -> Dict[str, Any]:
        """Reschedule an existing appointment."""
        try:
            logger.info(f"Rescheduling appointment {appointment_id}")
            
            # Get existing appointment
            appointment = await self._get_appointment(appointment_id)
            if not appointment:
                return {"status": "error", "error": "Appointment not found"}
            
            # Parse new date and time
            new_datetime = self._parse_datetime(new_date, new_time)
            if not new_datetime:
                return {"status": "error", "error": "Invalid date/time format"}
            
            # Check availability
            is_available = await self._check_availability(new_datetime, appointment["duration_minutes"])
            if not is_available:
                alternatives = await self._suggest_alternative_times(new_datetime, appointment["duration_minutes"])
                return {
                    "status": "conflict",
                    "message": "New time slot is not available",
                    "alternatives": alternatives
                }
            
            # Update appointment
            updated_appointment = await self._update_appointment(appointment_id, {
                "scheduled_at": new_datetime.isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            # Update calendar event
            calendar_updated = await self._update_calendar_event(
                appointment["calendar_event_id"], new_datetime
            )
            
            # Send reschedule notification
            notification_sent = await self._send_reschedule_notification(
                appointment["customer_email"], appointment, new_datetime
            )
            
            return {
                "status": "success",
                "appointment_id": appointment_id,
                "old_time": appointment["scheduled_at"],
                "new_time": new_datetime.isoformat(),
                "calendar_updated": calendar_updated,
                "notification_sent": notification_sent
            }
            
        except Exception as e:
            logger.error(f"Failed to reschedule appointment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an appointment."""
        try:
            logger.info(f"Cancelling appointment {appointment_id}")
            
            # Get appointment
            appointment = await self._get_appointment(appointment_id)
            if not appointment:
                return {"status": "error", "error": "Appointment not found"}
            
            # Update appointment status
            cancelled_appointment = await self._update_appointment(appointment_id, {
                "status": "cancelled",
                "cancellation_reason": reason,
                "cancelled_at": datetime.now().isoformat()
            })
            
            # Cancel calendar event
            calendar_cancelled = await self._cancel_calendar_event(appointment["calendar_event_id"])
            
            # Send cancellation notification
            notification_sent = await self._send_cancellation_notification(
                appointment["customer_email"], appointment, reason
            )
            
            return {
                "status": "success",
                "appointment_id": appointment_id,
                "cancelled_at": datetime.now().isoformat(),
                "reason": reason,
                "calendar_cancelled": calendar_cancelled,
                "notification_sent": notification_sent
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_availability(self, date: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get available time slots for a specific date."""
        try:
            logger.info(f"Getting availability for {date}")
            
            # Parse date
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Get business hours (9 AM to 5 PM)
            business_start = datetime.combine(target_date, datetime.min.time().replace(hour=9))
            business_end = datetime.combine(target_date, datetime.min.time().replace(hour=17))
            
            # Get existing appointments for the date
            existing_appointments = await self._get_appointments_for_date(target_date)
            
            # Generate available slots
            available_slots = []
            current_time = business_start
            
            while current_time + timedelta(minutes=duration_minutes) <= business_end:
                # Check if this slot conflicts with existing appointments
                is_free = True
                for appointment in existing_appointments:
                    apt_start = datetime.fromisoformat(appointment["scheduled_at"])
                    apt_end = apt_start + timedelta(minutes=appointment["duration_minutes"])
                    
                    slot_end = current_time + timedelta(minutes=duration_minutes)
                    
                    # Check for overlap
                    if (current_time < apt_end and slot_end > apt_start):
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append({
                        "start_time": current_time.strftime("%H:%M"),
                        "end_time": (current_time + timedelta(minutes=duration_minutes)).strftime("%H:%M"),
                        "datetime": current_time.isoformat()
                    })
                
                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)
            
            return {
                "status": "success",
                "date": date,
                "duration_minutes": duration_minutes,
                "available_slots": available_slots,
                "total_slots": len(available_slots)
            }
            
        except Exception as e:
            logger.error(f"Failed to get availability: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_appointments(self, customer_email: Optional[str] = None, 
                              date_from: Optional[str] = None, 
                              date_to: Optional[str] = None) -> Dict[str, Any]:
        """List appointments with optional filters."""
        try:
            logger.info(f"Listing appointments for {customer_email or 'all customers'}")
            
            filters = {}
            if customer_email:
                customer = await self.supabase_service.get_customer_by_email(customer_email)
                if customer:
                    filters["customer_id"] = customer["id"]
            
            if date_from:
                filters["date_from"] = date_from
            if date_to:
                filters["date_to"] = date_to
            
            appointments = await self._get_appointments_with_filters(filters)
            
            return {
                "status": "success",
                "appointments": appointments,
                "total_count": len(appointments),
                "filters_applied": filters
            }
            
        except Exception as e:
            logger.error(f"Failed to list appointments: {e}")
            return {"status": "error", "error": str(e)}
    
    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time strings into datetime object."""
        try:
            # Support various date formats
            date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
            time_formats = ["%H:%M", "%I:%M %p", "%H:%M:%S"]
            
            parsed_date = None
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, date_format).date()
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                return None
            
            parsed_time = None
            for time_format in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, time_format).time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                return None
            
            return datetime.combine(parsed_date, parsed_time)
            
        except Exception as e:
            logger.error(f"Failed to parse datetime: {e}")
            return None
    
    async def _check_availability(self, datetime_obj: datetime, duration_minutes: int) -> bool:
        """Check if a time slot is available."""
        try:
            # Get appointments for the date
            appointments = await self._get_appointments_for_date(datetime_obj.date())
            
            slot_end = datetime_obj + timedelta(minutes=duration_minutes)
            
            for appointment in appointments:
                apt_start = datetime.fromisoformat(appointment["scheduled_at"])
                apt_end = apt_start + timedelta(minutes=appointment["duration_minutes"])
                
                # Check for overlap
                if (datetime_obj < apt_end and slot_end > apt_start):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return False
    
    async def _suggest_alternative_times(self, requested_time: datetime, 
                                       duration_minutes: int) -> List[Dict[str, Any]]:
        """Suggest alternative time slots."""
        try:
            alternatives = []
            
            # Check same day, different times
            same_day_availability = await self.get_availability(
                requested_time.strftime("%Y-%m-%d"), duration_minutes
            )
            
            if same_day_availability["status"] == "success":
                for slot in same_day_availability["available_slots"][:3]:  # Top 3 alternatives
                    alternatives.append({
                        "date": requested_time.strftime("%Y-%m-%d"),
                        "time": slot["start_time"],
                        "datetime": slot["datetime"]
                    })
            
            # Check next few days if same day has no availability
            if len(alternatives) < 3:
                for i in range(1, 8):  # Check next 7 days
                    next_date = requested_time + timedelta(days=i)
                    next_day_availability = await self.get_availability(
                        next_date.strftime("%Y-%m-%d"), duration_minutes
                    )
                    
                    if next_day_availability["status"] == "success" and next_day_availability["available_slots"]:
                        # Add first available slot of the day
                        slot = next_day_availability["available_slots"][0]
                        alternatives.append({
                            "date": next_date.strftime("%Y-%m-%d"),
                            "time": slot["start_time"],
                            "datetime": slot["datetime"]
                        })
                        
                        if len(alternatives) >= 5:  # Limit to 5 alternatives
                            break
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Failed to suggest alternatives: {e}")
            return []
    
    # Mock database operations (to be replaced with actual Supabase operations)
    async def _create_appointment_record(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create appointment record in database."""
        # This would be implemented with actual Supabase operations
        return {"id": f"apt_{datetime.now().timestamp()}", **appointment_data}
    
    async def _get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        # Mock implementation
        return None
    
    async def _update_appointment(self, appointment_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update appointment record."""
        # Mock implementation
        return {"id": appointment_id, **updates}
    
    async def _get_appointments_for_date(self, date) -> List[Dict[str, Any]]:
        """Get all appointments for a specific date."""
        # Mock implementation
        return []
    
    async def _get_appointments_with_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get appointments with filters."""
        # Mock implementation
        return []
    
    async def _create_calendar_event(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event (Google Calendar, Outlook, etc.)."""
        # Mock implementation
        return {"id": f"cal_{datetime.now().timestamp()}"}
    
    async def _update_calendar_event(self, event_id: str, new_datetime: datetime) -> bool:
        """Update calendar event."""
        # Mock implementation
        return True
    
    async def _cancel_calendar_event(self, event_id: str) -> bool:
        """Cancel calendar event."""
        # Mock implementation
        return True
    
    async def _send_appointment_confirmation(self, customer_email: str, 
                                           appointment_data: Dict[str, Any]) -> bool:
        """Send appointment confirmation email."""
        # Mock implementation
        logger.info(f"Sending confirmation to {customer_email}")
        return True
    
    async def _send_reschedule_notification(self, customer_email: str, 
                                          appointment: Dict[str, Any], 
                                          new_datetime: datetime) -> bool:
        """Send reschedule notification."""
        # Mock implementation
        logger.info(f"Sending reschedule notification to {customer_email}")
        return True
    
    async def _send_cancellation_notification(self, customer_email: str, 
                                            appointment: Dict[str, Any], 
                                            reason: Optional[str]) -> bool:
        """Send cancellation notification."""
        # Mock implementation
        logger.info(f"Sending cancellation notification to {customer_email}")
        return True

    async def run(self, user_input: str) -> str:
        """Main entry point for calendar agent execution."""
        try:
            logger.info(f"Calendar agent processing: {user_input[:100]}...")
            
            # Try to parse as JSON command first
            try:
                command = json.loads(user_input)
                if isinstance(command, dict) and "action" in command:
                    return await self._handle_command(command)
            except json.JSONDecodeError:
                pass
            
            # Handle as natural language input
            return await self._handle_natural_language(user_input)
            
        except Exception as e:
            logger.error(f"Error in calendar agent run: {e}")
            return f"I encountered an error: {str(e)}. Please try again or contact support."
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "schedule_appointment":
            result = await self.schedule_appointment(
                customer_email=params.get("email"),
                appointment_type=params.get("type", "consultation"),
                preferred_date=params.get("date"),
                preferred_time=params.get("time"),
                duration_minutes=params.get("duration", 60)
            )
        elif action == "reschedule_appointment":
            result = await self.reschedule_appointment(
                appointment_id=params.get("appointment_id"),
                new_date=params.get("new_date"),
                new_time=params.get("new_time")
            )
        elif action == "cancel_appointment":
            result = await self.cancel_appointment(
                appointment_id=params.get("appointment_id"),
                reason=params.get("reason")
            )
        elif action == "get_availability":
            result = await self.get_availability(
                date=params.get("date"),
                duration_minutes=params.get("duration", 60)
            )
        elif action == "list_appointments":
            result = await self.list_appointments(
                customer_email=params.get("email"),
                date_from=params.get("date_from"),
                date_to=params.get("date_to")
            )
        else:
            return f"Unknown calendar action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input for calendar operations."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["schedule", "book", "appointment"]):
            return """📅 I can help you schedule an appointment! I need:

• Your email address
• Type of appointment (consultation, demo, support)
• Preferred date (YYYY-MM-DD format)
• Preferred time (HH:MM format)
• Duration (default: 60 minutes)

Example: "Schedule a consultation appointment for john@example.com on 2024-01-15 at 14:00"

Or use JSON format:
```json
{
  "action": "schedule_appointment",
  "params": {
    "email": "john@example.com",
    "type": "consultation",
    "date": "2024-01-15",
    "time": "14:00",
    "duration": 60
  }
}
```"""
        
        elif any(word in input_lower for word in ["availability", "available", "free"]):
            return """📅 I can check availability for you! Please provide:

• Date (YYYY-MM-DD format)
• Duration needed (optional, default: 60 minutes)

Example: "Check availability for 2024-01-15"

Or use JSON format:
```json
{
  "action": "get_availability",
  "params": {
    "date": "2024-01-15",
    "duration": 60
  }
}
```"""
        
        elif any(word in input_lower for word in ["reschedule", "change", "move"]):
            return """📅 I can help reschedule an appointment! I need:

• Appointment ID
• New date (YYYY-MM-DD format)
• New time (HH:MM format)

Use JSON format:
```json
{
  "action": "reschedule_appointment",
  "params": {
    "appointment_id": "apt_123",
    "new_date": "2024-01-16",
    "new_time": "15:00"
  }
}
```"""
        
        elif any(word in input_lower for word in ["cancel", "delete"]):
            return """📅 I can cancel an appointment for you! I need:

• Appointment ID
• Reason (optional)

Use JSON format:
```json
{
  "action": "cancel_appointment",
  "params": {
    "appointment_id": "apt_123",
    "reason": "Schedule conflict"
  }
}
```"""
        
        elif any(word in input_lower for word in ["list", "show", "appointments"]):
            return """📅 I can list appointments! Options:

• All appointments
• Appointments for specific customer
• Appointments in date range

Use JSON format:
```json
{
  "action": "list_appointments",
  "params": {
    "email": "customer@example.com",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31"
  }
}
```"""
        
        else:
            return """📅 **Calendar Agent** - I can help you with:

• **Schedule appointments** - Book new meetings and consultations
• **Check availability** - See available time slots
• **Reschedule appointments** - Change existing appointment times
• **Cancel appointments** - Cancel scheduled meetings
• **List appointments** - View scheduled appointments

What would you like to do with your calendar today?"""