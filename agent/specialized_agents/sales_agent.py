"""Sales Agent for customer relations, lead management, and ongoing support."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.adk.agents.base_agent import BaseAgent

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from my_adk_agent.services import (
    SupabaseService,
    LivekitService,
    StripeService,
)

logger = logging.getLogger(__name__)


class SalesAgent(BaseAgent):
    """ADK Agent specialized in sales, customer relations, and ongoing support."""
    
    def __init__(self):
        """Initialize the sales agent."""
        super().__init__(
            name="sales_agent",
            description="ADK Agent for managing sales processes, customer relations, and ongoing support"
        )
        
        # Initialize services
        object.__setattr__(self, 'supabase_service', SupabaseService())
        object.__setattr__(self, 'livekit_service', LivekitService())
        object.__setattr__(self, 'stripe_service', StripeService())
        
        logger.info("SalesAgent initialized")
    
    async def qualify_lead(self, customer_email: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a new lead based on provided information."""
        try:
            logger.info(f"Qualifying lead: {customer_email}")
            
            # Extract lead qualification criteria
            budget = lead_data.get("budget", "unknown")
            timeline = lead_data.get("timeline", "unknown")
            company_size = lead_data.get("company_size", "unknown")
            service_type = lead_data.get("service_type", "unknown")
            decision_maker = lead_data.get("is_decision_maker", False)
            
            # Calculate lead score
            score = 0
            qualification_notes = []
            
            # Budget scoring
            if budget in ["enterprise", "high"]:
                score += 30
                qualification_notes.append("✅ High budget potential")
            elif budget in ["standard", "medium"]:
                score += 20
                qualification_notes.append("✅ Standard budget range")
            elif budget == "low":
                score += 10
                qualification_notes.append("⚠️ Low budget - may need basic package")
            else:
                qualification_notes.append("❓ Budget not specified")
            
            # Timeline scoring
            if timeline in ["urgent", "immediate"]:
                score += 25
                qualification_notes.append("✅ Urgent timeline - high priority")
            elif timeline in ["standard", "flexible"]:
                score += 15
                qualification_notes.append("✅ Flexible timeline")
            else:
                qualification_notes.append("❓ Timeline not specified")
            
            # Decision maker scoring
            if decision_maker:
                score += 20
                qualification_notes.append("✅ Decision maker identified")
            else:
                score += 5
                qualification_notes.append("⚠️ May need to identify decision maker")
            
            # Service type scoring
            if service_type in ["ai_agent", "workflow_automation"]:
                score += 15
                qualification_notes.append("✅ High-value service type")
            elif service_type == "chatbot":
                score += 10
                qualification_notes.append("✅ Standard service type")
            
            # Company size scoring
            if company_size in ["enterprise", "large"]:
                score += 10
                qualification_notes.append("✅ Enterprise client")
            elif company_size == "medium":
                score += 5
                qualification_notes.append("✅ Medium business")
            
            # Determine qualification level
            if score >= 70:
                qualification = "hot"
                priority = "high"
                next_action = "Schedule demo immediately"
            elif score >= 50:
                qualification = "warm"
                priority = "medium"
                next_action = "Schedule consultation call"
            elif score >= 30:
                qualification = "cold"
                priority = "low"
                next_action = "Send information packet"
            else:
                qualification = "unqualified"
                priority = "very_low"
                next_action = "Nurture with content marketing"
            
            # Create lead record
            lead_record = {
                "customer_email": customer_email,
                "qualification": qualification,
                "score": score,
                "priority": priority,
                "next_action": next_action,
                "qualification_notes": qualification_notes,
                "lead_data": lead_data,
                "qualified_at": datetime.now().isoformat(),
                "status": "qualified"
            }
            
            # Store lead record
            stored_lead = await self._store_lead_record(lead_record)
            
            return {
                "status": "success",
                "qualification": qualification,
                "score": score,
                "priority": priority,
                "next_action": next_action,
                "qualification_notes": qualification_notes,
                "lead_id": stored_lead.get("id") if stored_lead else None
            }
            
        except Exception as e:
            logger.error(f"Failed to qualify lead: {e}")
            return {"status": "error", "error": str(e)}
    
    async def manage_sales_pipeline(self, customer_email: str, stage: str, 
                                  notes: Optional[str] = None) -> Dict[str, Any]:
        """Manage customer through sales pipeline stages."""
        try:
            logger.info(f"Managing sales pipeline for {customer_email}: {stage}")
            
            # Define pipeline stages
            pipeline_stages = [
                "lead",
                "qualified",
                "demo_scheduled",
                "demo_completed",
                "proposal_sent",
                "negotiation",
                "closed_won",
                "closed_lost"
            ]
            
            if stage not in pipeline_stages:
                return {"status": "error", "error": f"Invalid stage: {stage}"}
            
            # Get current customer record
            customer = await self.supabase_service.get_customer_by_email(customer_email)
            if not customer:
                return {"status": "error", "error": "Customer not found"}
            
            # Update pipeline stage
            pipeline_update = {
                "stage": stage,
                "stage_updated_at": datetime.now().isoformat(),
                "notes": notes
            }
            
            # Stage-specific actions
            stage_actions = await self._execute_stage_actions(customer_email, stage)
            
            # Update customer record
            updated_customer = await self._update_customer_pipeline(customer_email, pipeline_update)
            
            # Calculate stage metrics
            stage_metrics = await self._calculate_stage_metrics(stage)
            
            return {
                "status": "success",
                "customer_email": customer_email,
                "previous_stage": customer.get("pipeline_stage", "unknown"),
                "current_stage": stage,
                "stage_actions": stage_actions,
                "stage_metrics": stage_metrics,
                "updated_at": pipeline_update["stage_updated_at"]
            }
            
        except Exception as e:
            logger.error(f"Failed to manage sales pipeline: {e}")
            return {"status": "error", "error": str(e)}
    
    async def coordinate_user_testing(self, customer_email: str, 
                                    requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate user acceptance testing with the customer."""
        try:
            logger.info(f"Coordinating user testing for: {customer_email}")
            
            # Create testing plan
            testing_plan = await self._create_testing_plan(requirements)
            
            # Schedule testing session
            testing_session = await self._schedule_testing_session(customer_email, testing_plan)
            
            # Prepare testing environment
            test_environment = await self._prepare_test_environment(customer_email, requirements)
            
            # Send testing instructions
            instructions_sent = await self._send_testing_instructions(customer_email, testing_plan)
            
            return {
                "status": "success",
                "customer_email": customer_email,
                "testing_plan": testing_plan,
                "testing_session": testing_session,
                "test_environment": test_environment,
                "instructions_sent": instructions_sent,
                "next_steps": [
                    "Customer will receive testing instructions",
                    "Testing session scheduled",
                    "Results will be collected and analyzed",
                    "Feedback will be incorporated into final delivery"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to coordinate user testing: {e}")
            return {"status": "error", "error": str(e)}
    
    async def setup_ongoing_support(self, customer_email: str, 
                                  project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up ongoing support and maintenance for delivered projects."""
        try:
            logger.info(f"Setting up ongoing support for: {customer_email}")
            
            service_type = project_data.get("service_type", "unknown")
            complexity = project_data.get("complexity", "medium")
            
            # Determine support tier
            support_tier = await self._determine_support_tier(service_type, complexity)
            
            # Create support package
            support_package = await self._create_support_package(support_tier, project_data)
            
            # Set up monitoring
            monitoring_setup = await self._setup_project_monitoring(customer_email, project_data)
            
            # Create support documentation
            documentation = await self._create_support_documentation(customer_email, project_data)
            
            # Schedule regular check-ins
            check_ins = await self._schedule_support_check_ins(customer_email, support_tier)
            
            return {
                "status": "success",
                "customer_email": customer_email,
                "support_tier": support_tier,
                "support_package": support_package,
                "monitoring_setup": monitoring_setup,
                "documentation": documentation,
                "scheduled_check_ins": check_ins,
                "support_contact": "support@consulting.sa"
            }
            
        except Exception as e:
            logger.error(f"Failed to setup ongoing support: {e}")
            return {"status": "error", "error": str(e)}
    
    async def handle_customer_feedback(self, customer_email: str, 
                                     feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and process customer feedback."""
        try:
            logger.info(f"Processing feedback from: {customer_email}")
            
            feedback_type = feedback_data.get("type", "general")
            rating = feedback_data.get("rating", 0)
            comments = feedback_data.get("comments", "")
            category = feedback_data.get("category", "general")
            
            # Analyze feedback sentiment
            sentiment_analysis = await self._analyze_feedback_sentiment(comments)
            
            # Categorize feedback
            feedback_category = await self._categorize_feedback(feedback_data)
            
            # Determine required actions
            required_actions = await self._determine_feedback_actions(feedback_data, sentiment_analysis)
            
            # Create feedback record
            feedback_record = {
                "customer_email": customer_email,
                "type": feedback_type,
                "rating": rating,
                "comments": comments,
                "category": feedback_category,
                "sentiment": sentiment_analysis,
                "required_actions": required_actions,
                "received_at": datetime.now().isoformat(),
                "status": "received"
            }
            
            # Store feedback
            stored_feedback = await self._store_feedback_record(feedback_record)
            
            # Execute immediate actions if needed
            if rating <= 2 or sentiment_analysis.get("score", 0) < -0.5:  # Negative feedback
                immediate_actions = await self._handle_negative_feedback(customer_email, feedback_record)
            else:
                immediate_actions = await self._handle_positive_feedback(customer_email, feedback_record)
            
            return {
                "status": "success",
                "feedback_id": stored_feedback.get("id") if stored_feedback else None,
                "sentiment": sentiment_analysis,
                "category": feedback_category,
                "required_actions": required_actions,
                "immediate_actions": immediate_actions,
                "follow_up_scheduled": rating <= 3  # Schedule follow-up for ratings 3 and below
            }
            
        except Exception as e:
            logger.error(f"Failed to handle customer feedback: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_sales_report(self, period: str = "monthly") -> Dict[str, Any]:
        """Generate sales performance report."""
        try:
            logger.info(f"Generating {period} sales report")
            
            # Calculate date range
            end_date = datetime.now()
            if period == "daily":
                start_date = end_date - timedelta(days=1)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            elif period == "quarterly":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)  # Default to monthly
            
            # Get sales data
            sales_data = await self._get_sales_data(start_date, end_date)
            
            # Calculate metrics
            metrics = {
                "total_leads": len(sales_data.get("leads", [])),
                "qualified_leads": len([l for l in sales_data.get("leads", []) if l.get("qualification") in ["hot", "warm"]]),
                "demos_scheduled": len([l for l in sales_data.get("leads", []) if l.get("stage") == "demo_scheduled"]),
                "proposals_sent": len([l for l in sales_data.get("leads", []) if l.get("stage") == "proposal_sent"]),
                "deals_closed": len([l for l in sales_data.get("leads", []) if l.get("stage") == "closed_won"]),
                "deals_lost": len([l for l in sales_data.get("leads", []) if l.get("stage") == "closed_lost"]),
                "conversion_rate": 0,
                "average_deal_size": 0,
                "total_revenue": 0
            }
            
            # Calculate conversion rate
            if metrics["total_leads"] > 0:
                metrics["conversion_rate"] = (metrics["deals_closed"] / metrics["total_leads"]) * 100
            
            # Calculate revenue metrics
            closed_deals = [l for l in sales_data.get("leads", []) if l.get("stage") == "closed_won"]
            if closed_deals:
                deal_values = [deal.get("deal_value", 0) for deal in closed_deals]
                metrics["total_revenue"] = sum(deal_values)
                metrics["average_deal_size"] = metrics["total_revenue"] / len(closed_deals)
            
            # Generate insights
            insights = await self._generate_sales_insights(metrics, sales_data)
            
            return {
                "status": "success",
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics": metrics,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate sales report: {e}")
            return {"status": "error", "error": str(e)}
    
    # Helper methods
    async def _execute_stage_actions(self, customer_email: str, stage: str) -> List[str]:
        """Execute actions specific to pipeline stage."""
        actions = []
        
        if stage == "demo_scheduled":
            actions.append("Send demo preparation email")
            actions.append("Create demo environment")
            actions.append("Prepare demo script")
        elif stage == "demo_completed":
            actions.append("Send follow-up email")
            actions.append("Prepare proposal")
            actions.append("Schedule proposal review")
        elif stage == "proposal_sent":
            actions.append("Schedule follow-up call")
            actions.append("Track proposal engagement")
        elif stage == "closed_won":
            actions.append("Initiate project kickoff")
            actions.append("Send welcome package")
            actions.append("Setup customer success")
        
        return actions
    
    async def _create_testing_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create user acceptance testing plan."""
        service_type = requirements.get("service_type", "unknown")
        
        if service_type == "chatbot":
            test_scenarios = [
                "Basic conversation flow",
                "FAQ handling",
                "Error scenarios",
                "Integration testing"
            ]
        elif service_type == "ai_agent":
            test_scenarios = [
                "Task execution",
                "Decision making",
                "Integration workflows",
                "Performance testing"
            ]
        else:
            test_scenarios = [
                "Core functionality",
                "User interface",
                "Integration testing",
                "Performance validation"
            ]
        
        return {
            "service_type": service_type,
            "test_scenarios": test_scenarios,
            "estimated_duration": "2-4 hours",
            "testing_environment": "staging",
            "success_criteria": "90% test scenarios pass"
        }
    
    async def _analyze_feedback_sentiment(self, comments: str) -> Dict[str, Any]:
        """Analyze sentiment of feedback comments."""
        # Simple sentiment analysis (would use actual NLP in production)
        positive_words = ["good", "great", "excellent", "amazing", "love", "perfect"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible"]
        
        comment_lower = comments.lower()
        positive_count = sum(1 for word in positive_words if word in comment_lower)
        negative_count = sum(1 for word in negative_words if word in comment_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.5
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -0.5
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": 0.7  # Mock confidence score
        }
    
    # Mock database operations
    async def _store_lead_record(self, lead_record: Dict[str, Any]) -> Dict[str, Any]:
        """Store lead record in database."""
        return {"id": f"lead_{datetime.now().timestamp()}", **lead_record}
    
    async def _update_customer_pipeline(self, customer_email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer pipeline stage."""
        return {"email": customer_email, **updates}
    
    async def _calculate_stage_metrics(self, stage: str) -> Dict[str, Any]:
        """Calculate metrics for pipeline stage."""
        return {
            "stage": stage,
            "average_time_in_stage": "3 days",
            "conversion_rate": "65%",
            "total_in_stage": 5
        }
    
    async def _get_sales_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get sales data for date range."""
        return {
            "leads": [],  # Would fetch from database
            "deals": [],
            "activities": []
        }
    
    async def _generate_sales_insights(self, metrics: Dict[str, Any], sales_data: Dict[str, Any]) -> List[str]:
        """Generate insights from sales data."""
        insights = []
        
        if metrics["conversion_rate"] > 20:
            insights.append("✅ Conversion rate is above industry average")
        else:
            insights.append("⚠️ Conversion rate needs improvement")
        
        if metrics["total_leads"] > 10:
            insights.append("✅ Strong lead generation")
        else:
            insights.append("📈 Focus on lead generation activities")
        
        return insights
    
    async def run(self, user_input: str) -> str:
        """Main entry point for sales agent execution."""
        try:
            logger.info(f"Sales agent processing: {user_input[:100]}...")
            
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
            logger.error(f"Error in sales agent run: {e}")
            return f"I encountered an error: {str(e)}. Please try again or contact support."
    
    async def _handle_command(self, command: Dict[str, Any]) -> str:
        """Handle structured JSON commands."""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "qualify_lead":
            result = await self.qualify_lead(
                customer_email=params.get("email"),
                lead_data=params.get("lead_data", {})
            )
        elif action == "manage_pipeline":
            result = await self.manage_sales_pipeline(
                customer_email=params.get("email"),
                stage=params.get("stage"),
                notes=params.get("notes")
            )
        elif action == "coordinate_testing":
            result = await self.coordinate_user_testing(
                customer_email=params.get("email"),
                requirements=params.get("requirements", {})
            )
        elif action == "setup_support":
            result = await self.setup_ongoing_support(
                customer_email=params.get("email"),
                project_data=params.get("project_data", {})
            )
        elif action == "handle_feedback":
            result = await self.handle_customer_feedback(
                customer_email=params.get("email"),
                feedback_data=params.get("feedback_data", {})
            )
        elif action == "generate_report":
            result = await self.generate_sales_report(
                period=params.get("period", "monthly")
            )
        else:
            return f"Unknown sales action: {action}"
        
        return json.dumps(result, indent=2)
    
    async def _handle_natural_language(self, user_input: str) -> str:
        """Handle natural language input for sales operations."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["lead", "qualify", "prospect"]):
            return """🎯 **Sales Agent** - Lead Management

I can help you qualify and manage leads:

**Lead Qualification:**
• Analyze lead potential and scoring
• Determine priority and next actions
• Track through sales pipeline

**Pipeline Management:**
• Move leads through sales stages
• Track conversion metrics
• Generate sales reports

Use JSON format:
```json
{
  "action": "qualify_lead",
  "params": {
    "email": "prospect@example.com",
    "lead_data": {
      "budget": "standard",
      "timeline": "urgent",
      "service_type": "chatbot",
      "is_decision_maker": true
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["pipeline", "stage", "sales"]):
            return """📊 **Sales Pipeline Management**

I manage customers through these stages:
• **Lead** - Initial contact
• **Qualified** - Meets criteria
• **Demo Scheduled** - Demo booked
• **Demo Completed** - Demo finished
• **Proposal Sent** - Proposal delivered
• **Negotiation** - In discussion
• **Closed Won** - Deal closed
• **Closed Lost** - Deal lost

Use JSON format:
```json
{
  "action": "manage_pipeline",
  "params": {
    "email": "customer@example.com",
    "stage": "demo_completed",
    "notes": "Great demo, ready for proposal"
  }
}
```"""
        
        elif any(word in input_lower for word in ["testing", "uat", "user acceptance"]):
            return """🧪 **User Acceptance Testing**

I coordinate UAT with customers:
• Create testing plans
• Schedule testing sessions
• Prepare test environments
• Collect and analyze feedback

Use JSON format:
```json
{
  "action": "coordinate_testing",
  "params": {
    "email": "customer@example.com",
    "requirements": {
      "service_type": "chatbot",
      "complexity": "medium"
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["support", "maintenance", "ongoing"]):
            return """🛠️ **Ongoing Support Setup**

I set up post-delivery support:
• Determine support tier
• Create support packages
• Setup monitoring
• Schedule regular check-ins

Use JSON format:
```json
{
  "action": "setup_support",
  "params": {
    "email": "customer@example.com",
    "project_data": {
      "service_type": "ai_agent",
      "complexity": "high"
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["feedback", "review", "rating"]):
            return """💬 **Customer Feedback Management**

I handle customer feedback:
• Analyze sentiment
• Categorize feedback
• Determine required actions
• Handle negative feedback immediately

Use JSON format:
```json
{
  "action": "handle_feedback",
  "params": {
    "email": "customer@example.com",
    "feedback_data": {
      "type": "project_review",
      "rating": 4,
      "comments": "Great work, minor improvements needed",
      "category": "quality"
    }
  }
}
```"""
        
        elif any(word in input_lower for word in ["report", "metrics", "analytics"]):
            return """📈 **Sales Reporting**

I generate comprehensive sales reports:
• Lead generation metrics
• Conversion rates
• Revenue analysis
• Pipeline performance
• Insights and recommendations

Use JSON format:
```json
{
  "action": "generate_report",
  "params": {
    "period": "monthly"
  }
}
```

Available periods: daily, weekly, monthly, quarterly"""
        
        else:
            return """💼 **Sales Agent** - Customer Relations & Support

I handle all sales and customer success activities:

**🎯 Lead Management:**
• Qualify new leads and prospects
• Score leads based on criteria
• Manage sales pipeline stages

**📊 Pipeline Management:**
• Track customers through sales stages
• Calculate conversion metrics
• Generate sales reports

**🧪 Testing Coordination:**
• Coordinate user acceptance testing
• Collect and analyze feedback
• Ensure customer satisfaction

**🛠️ Ongoing Support:**
• Set up post-delivery support
• Create maintenance packages
• Schedule regular check-ins

**💬 Customer Success:**
• Handle customer feedback
• Manage customer relationships
• Ensure long-term satisfaction

What sales activity can I help you with today?"""