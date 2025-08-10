"""
Task and Calendar Management Service
Using latest Python libraries for integrated task and calendar management
"""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
import logging
import uuid
import json
from dateutil import parser, rrule
from dateutil.relativedelta import relativedelta
import pytz
from icalendar import Calendar, Event, vDDDTypes
import caldav
from caldav import DAVClient
import sqlite3
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel, Field
import arrow

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EventType(Enum):
    """Calendar event type enumeration"""
    MEETING = "meeting"
    CONSULTATION = "consultation"
    DEADLINE = "deadline"
    REMINDER = "reminder"
    MILESTONE = "milestone"


@dataclass
class Task:
    """Task data structure with comprehensive fields"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: str = ""
    customer_id: str = ""
    project_id: str = ""
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    subtasks: List[str] = field(default_factory=list)  # Task IDs
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    event_type: EventType = EventType.MEETING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    timezone: str = "Asia/Riyadh"  # Default to Saudi timezone
    location: str = ""
    attendees: List[Dict[str, Any]] = field(default_factory=list)
    organizer: Dict[str, Any] = field(default_factory=dict)
    customer_id: str = ""
    project_id: str = ""
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "confirmed"  # confirmed, tentative, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskCalendarService:
    """Comprehensive task and calendar management service"""
    
    def __init__(self, database_path: str = "task_calendar.db"):
        self.database_path = database_path
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone("Asia/Riyadh")
        self._init_database()
        self._start_scheduler()
    
    def _init_database(self):
        """Initialize SQLite database for tasks and events"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                assignee_id TEXT,
                customer_id TEXT,
                project_id TEXT,
                tags TEXT,  -- JSON array
                due_date TEXT,  -- ISO format
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                dependencies TEXT,  -- JSON array
                subtasks TEXT,  -- JSON array
                attachments TEXT,  -- JSON array
                comments TEXT,  -- JSON array
                metadata TEXT  -- JSON object
            )
        """)
        
        # Calendar events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                event_type TEXT NOT NULL,
                start_time TEXT NOT NULL,  -- ISO format
                end_time TEXT NOT NULL,  -- ISO format
                timezone TEXT NOT NULL,
                location TEXT,
                attendees TEXT,  -- JSON array
                organizer TEXT,  -- JSON object
                customer_id TEXT,
                project_id TEXT,
                is_recurring BOOLEAN,
                recurrence_rule TEXT,
                reminders TEXT,  -- JSON array
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT  -- JSON object
            )
        """)
        
        # Task dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                depends_on_task_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (depends_on_task_id) REFERENCES tasks (id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_customer_id ON tasks (customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks (project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_customer_id ON calendar_events (customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_time ON calendar_events (start_time)")
        
        conn.commit()
        conn.close()
    
    def _start_scheduler(self):
        """Start the async scheduler for reminders and recurring tasks"""
        if not self.scheduler.running:
            self.scheduler.start()
    
    # Task Management Methods
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task"""
        task = Task(
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=TaskStatus(task_data.get("status", "pending")),
            priority=TaskPriority(task_data.get("priority", "medium")),
            assignee_id=task_data.get("assignee_id", ""),
            customer_id=task_data.get("customer_id", ""),
            project_id=task_data.get("project_id", ""),
            tags=task_data.get("tags", []),
            due_date=parser.parse(task_data["due_date"]) if task_data.get("due_date") else None,
            estimated_hours=task_data.get("estimated_hours"),
            dependencies=task_data.get("dependencies", []),
            metadata=task_data.get("metadata", {})
        )
        
        self._save_task(task)
        
        # Schedule reminder if due date is set
        if task.due_date:
            self._schedule_task_reminder(task)
        
        logger.info(f"Created task: {task.id} - {task.title}")
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update an existing task"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        # Update fields
        for field_name, value in updates.items():
            if hasattr(task, field_name):
                if field_name == "status":
                    task.status = TaskStatus(value)
                elif field_name == "priority":
                    task.priority = TaskPriority(value)
                elif field_name == "due_date" and value:
                    task.due_date = parser.parse(value) if isinstance(value, str) else value
                else:
                    setattr(task, field_name, value)
        
        task.updated_at = datetime.now()
        
        # Mark as completed if status changed to completed
        if task.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now()
        
        self._save_task(task)
        
        # Update reminder if due date changed
        if "due_date" in updates and task.due_date:
            self._schedule_task_reminder(task)
        
        logger.info(f"Updated task: {task.id}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_task(row)
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[Task]:
        """Get tasks with optional filters"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks"
        params = []
        
        if filters:
            conditions = []
            if "customer_id" in filters:
                conditions.append("customer_id = ?")
                params.append(filters["customer_id"])
            if "project_id" in filters:
                conditions.append("project_id = ?")
                params.append(filters["project_id"])
            if "status" in filters:
                conditions.append("status = ?")
                params.append(filters["status"])
            if "assignee_id" in filters:
                conditions.append("assignee_id = ?")
                params.append(filters["assignee_id"])
            if "due_before" in filters:
                conditions.append("due_date <= ?")
                params.append(filters["due_before"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_task(row) for row in rows]
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        cursor.execute("DELETE FROM task_dependencies WHERE task_id = ? OR depends_on_task_id = ?", 
                      (task_id, task_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"Deleted task: {task_id}")
        
        return deleted
    
    # Calendar Management Methods
    
    def create_event(self, event_data: Dict[str, Any]) -> CalendarEvent:
        """Create a new calendar event"""
        start_time = parser.parse(event_data["start_time"]) if isinstance(event_data["start_time"], str) else event_data["start_time"]
        end_time = parser.parse(event_data["end_time"]) if isinstance(event_data["end_time"], str) else event_data["end_time"]
        
        event = CalendarEvent(
            title=event_data["title"],
            description=event_data.get("description", ""),
            event_type=EventType(event_data.get("event_type", "meeting")),
            start_time=start_time,
            end_time=end_time,
            timezone=event_data.get("timezone", "Asia/Riyadh"),
            location=event_data.get("location", ""),
            attendees=event_data.get("attendees", []),
            organizer=event_data.get("organizer", {}),
            customer_id=event_data.get("customer_id", ""),
            project_id=event_data.get("project_id", ""),
            is_recurring=event_data.get("is_recurring", False),
            recurrence_rule=event_data.get("recurrence_rule"),
            reminders=event_data.get("reminders", []),
            metadata=event_data.get("metadata", {})
        )
        
        self._save_event(event)
        
        # Schedule reminders
        for reminder in event.reminders:
            self._schedule_event_reminder(event, reminder)
        
        # Create recurring events if needed
        if event.is_recurring and event.recurrence_rule:
            self._create_recurring_events(event)
        
        logger.info(f"Created event: {event.id} - {event.title}")
        return event
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Update an existing calendar event"""
        event = self.get_event(event_id)
        if not event:
            return None
        
        # Update fields
        for field_name, value in updates.items():
            if hasattr(event, field_name):
                if field_name in ["start_time", "end_time"] and isinstance(value, str):
                    setattr(event, field_name, parser.parse(value))
                elif field_name == "event_type":
                    event.event_type = EventType(value)
                else:
                    setattr(event, field_name, value)
        
        event.updated_at = datetime.now()
        self._save_event(event)
        
        logger.info(f"Updated event: {event.id}")
        return event
    
    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Get event by ID"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_event(row)
    
    def get_events(self, filters: Dict[str, Any] = None) -> List[CalendarEvent]:
        """Get events with optional filters"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM calendar_events"
        params = []
        
        if filters:
            conditions = []
            if "customer_id" in filters:
                conditions.append("customer_id = ?")
                params.append(filters["customer_id"])
            if "project_id" in filters:
                conditions.append("project_id = ?")
                params.append(filters["project_id"])
            if "start_date" in filters:
                conditions.append("start_time >= ?")
                params.append(filters["start_date"])
            if "end_date" in filters:
                conditions.append("start_time <= ?")
                params.append(filters["end_date"])
            if "event_type" in filters:
                conditions.append("event_type = ?")
                params.append(filters["event_type"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY start_time ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_event(row) for row in rows]
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"Deleted event: {event_id}")
        
        return deleted
    
    # Advanced Features
    
    def get_availability(self, start_date: date, end_date: date, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get available time slots for scheduling"""
        # Get existing events in the date range
        events = self.get_events({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        })
        
        # Business hours (9 AM to 6 PM, Sunday to Thursday for Saudi Arabia)
        business_hours = {
            6: (9, 18),  # Sunday
            0: (9, 18),  # Monday
            1: (9, 18),  # Tuesday
            2: (9, 18),  # Wednesday
            3: (9, 18),  # Thursday
            # Friday and Saturday are weekends
        }
        
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            weekday = current_date.weekday()
            
            if weekday in business_hours:
                start_hour, end_hour = business_hours[weekday]
                
                # Generate time slots for the day
                current_time = datetime.combine(current_date, datetime.min.time().replace(hour=start_hour))
                end_time = datetime.combine(current_date, datetime.min.time().replace(hour=end_hour))
                
                while current_time + timedelta(minutes=duration_minutes) <= end_time:
                    slot_end = current_time + timedelta(minutes=duration_minutes)
                    
                    # Check if slot conflicts with existing events
                    conflict = any(
                        event.start_time < slot_end and event.end_time > current_time
                        for event in events
                    )
                    
                    if not conflict:
                        available_slots.append({
                            "start_time": current_time.isoformat(),
                            "end_time": slot_end.isoformat(),
                            "duration_minutes": duration_minutes
                        })
                    
                    current_time += timedelta(minutes=30)  # 30-minute intervals
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def create_task_from_event(self, event_id: str, task_data: Dict[str, Any] = None) -> Optional[Task]:
        """Create a task from a calendar event"""
        event = self.get_event(event_id)
        if not event:
            return None
        
        task_info = {
            "title": task_data.get("title", f"Task: {event.title}"),
            "description": task_data.get("description", event.description),
            "customer_id": event.customer_id,
            "project_id": event.project_id,
            "due_date": event.start_time.isoformat(),
            "metadata": {"created_from_event": event_id}
        }
        
        if task_data:
            task_info.update(task_data)
        
        return self.create_task(task_info)
    
    def get_dashboard_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get dashboard summary for customer"""
        # Get tasks
        tasks = self.get_tasks({"customer_id": customer_id})
        task_stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "overdue": len([t for t in tasks if t.due_date and t.due_date < datetime.now() and t.status != TaskStatus.COMPLETED])
        }
        
        # Get upcoming events
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        upcoming_events = self.get_events({
            "customer_id": customer_id,
            "start_date": today.isoformat(),
            "end_date": next_week.isoformat()
        })
        
        return {
            "task_summary": task_stats,
            "upcoming_events": len(upcoming_events),
            "next_event": upcoming_events[0] if upcoming_events else None,
            "overdue_tasks": [t for t in tasks if t.due_date and t.due_date < datetime.now() and t.status != TaskStatus.COMPLETED][:5]
        }
    
    # Private Helper Methods
    
    def _save_task(self, task: Task):
        """Save task to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks 
            (id, title, description, status, priority, assignee_id, customer_id, project_id, 
             tags, due_date, created_at, updated_at, completed_at, estimated_hours, actual_hours,
             dependencies, subtasks, attachments, comments, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id, task.title, task.description, task.status.value, task.priority.value,
            task.assignee_id, task.customer_id, task.project_id,
            json.dumps(task.tags), task.due_date.isoformat() if task.due_date else None,
            task.created_at.isoformat(), task.updated_at.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None,
            task.estimated_hours, task.actual_hours,
            json.dumps(task.dependencies), json.dumps(task.subtasks),
            json.dumps(task.attachments), json.dumps(task.comments),
            json.dumps(task.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_event(self, event: CalendarEvent):
        """Save event to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO calendar_events 
            (id, title, description, event_type, start_time, end_time, timezone, location,
             attendees, organizer, customer_id, project_id, is_recurring, recurrence_rule,
             reminders, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id, event.title, event.description, event.event_type.value,
            event.start_time.isoformat(), event.end_time.isoformat(), event.timezone, event.location,
            json.dumps(event.attendees), json.dumps(event.organizer),
            event.customer_id, event.project_id, event.is_recurring, event.recurrence_rule,
            json.dumps(event.reminders), event.status,
            event.created_at.isoformat(), event.updated_at.isoformat(),
            json.dumps(event.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object"""
        return Task(
            id=row[0], title=row[1], description=row[2],
            status=TaskStatus(row[3]), priority=TaskPriority(row[4]),
            assignee_id=row[5], customer_id=row[6], project_id=row[7],
            tags=json.loads(row[8]) if row[8] else [],
            due_date=parser.parse(row[9]) if row[9] else None,
            created_at=parser.parse(row[10]), updated_at=parser.parse(row[11]),
            completed_at=parser.parse(row[12]) if row[12] else None,
            estimated_hours=row[13], actual_hours=row[14],
            dependencies=json.loads(row[15]) if row[15] else [],
            subtasks=json.loads(row[16]) if row[16] else [],
            attachments=json.loads(row[17]) if row[17] else [],
            comments=json.loads(row[18]) if row[18] else [],
            metadata=json.loads(row[19]) if row[19] else {}
        )
    
    def _row_to_event(self, row) -> CalendarEvent:
        """Convert database row to CalendarEvent object"""
        return CalendarEvent(
            id=row[0], title=row[1], description=row[2],
            event_type=EventType(row[3]),
            start_time=parser.parse(row[4]), end_time=parser.parse(row[5]),
            timezone=row[6], location=row[7],
            attendees=json.loads(row[8]) if row[8] else [],
            organizer=json.loads(row[9]) if row[9] else {},
            customer_id=row[10], project_id=row[11],
            is_recurring=bool(row[12]), recurrence_rule=row[13],
            reminders=json.loads(row[14]) if row[14] else [],
            status=row[15],
            created_at=parser.parse(row[16]), updated_at=parser.parse(row[17]),
            metadata=json.loads(row[18]) if row[18] else {}
        )
    
    def _schedule_task_reminder(self, task: Task):
        """Schedule reminder for task"""
        if not task.due_date:
            return
        
        # Schedule reminder 1 day before due date
        reminder_time = task.due_date - timedelta(days=1)
        
        if reminder_time > datetime.now():
            self.scheduler.add_job(
                self._send_task_reminder,
                DateTrigger(run_date=reminder_time),
                args=[task.id],
                id=f"task_reminder_{task.id}",
                replace_existing=True
            )
    
    def _schedule_event_reminder(self, event: CalendarEvent, reminder: Dict[str, Any]):
        """Schedule reminder for event"""
        reminder_minutes = reminder.get("minutes_before", 15)
        reminder_time = event.start_time - timedelta(minutes=reminder_minutes)
        
        if reminder_time > datetime.now():
            self.scheduler.add_job(
                self._send_event_reminder,
                DateTrigger(run_date=reminder_time),
                args=[event.id, reminder],
                id=f"event_reminder_{event.id}_{reminder_minutes}",
                replace_existing=True
            )
    
    def _create_recurring_events(self, base_event: CalendarEvent):
        """Create recurring events based on recurrence rule"""
        if not base_event.recurrence_rule:
            return
        
        # Parse recurrence rule and create events
        # This is a simplified implementation
        # In production, use a proper RRULE parser
        pass
    
    async def _send_task_reminder(self, task_id: str):
        """Send task reminder notification"""
        task = self.get_task(task_id)
        if task and task.status != TaskStatus.COMPLETED:
            # Send notification via notification service
            logger.info(f"Task reminder: {task.title} is due soon")
    
    async def _send_event_reminder(self, event_id: str, reminder: Dict[str, Any]):
        """Send event reminder notification"""
        event = self.get_event(event_id)
        if event:
            # Send notification via notification service
            logger.info(f"Event reminder: {event.title} starts in {reminder.get('minutes_before', 15)} minutes")