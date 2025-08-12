"""
Demo Data Generator for consulting.sa Multi-Agent System
Creates sample customers, workflows, projects, and consultations for testing
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

# Sample data for generating realistic demo content
SAMPLE_CUSTOMERS = [
    {
        "name": "أحمد محمد العلي",
        "email": "ahmed.ali@techcorp.sa",
        "phone": "00966501234567",
        "language": "ar",
        "business_domain": "التجارة الإلكترونية",
        "challenges": ["أتمتة خدمة العملاء", "تحليل البيانات", "تحسين المبيعات"],
        "company": "شركة التقنية المتقدمة"
    },
    {
        "name": "فاطمة سعد الغامدي",
        "email": "fatima.alghamdi@healthplus.sa",
        "phone": "00966502345678",
        "language": "ar",
        "business_domain": "الرعاية الصحية",
        "challenges": ["إدارة المواعيد", "تحليل البيانات الطبية", "تحسين تجربة المرضى"],
        "company": "مجمع الصحة الشامل"
    },
    {
        "name": "خالد عبدالله النمر",
        "email": "khalid.alnamir@edutech.sa",
        "phone": "00966503456789",
        "language": "ar",
        "business_domain": "التعليم",
        "challenges": ["منصة تعليمية ذكية", "تقييم الطلاب", "إدارة المحتوى"],
        "company": "منصة التعليم الذكي"
    },
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@globaltech.com",
        "phone": "00966504567890",
        "language": "en",
        "business_domain": "Financial Services",
        "challenges": ["Risk Assessment", "Fraud Detection", "Customer Analytics"],
        "company": "Global Financial Solutions"
    },
    {
        "name": "محمد عبدالرحمن الشهري",
        "email": "mohammed.alshehri@logistics.sa",
        "phone": "00966505678901",
        "language": "ar",
        "business_domain": "اللوجستيات",
        "challenges": ["تتبع الشحنات", "تحسين المسارات", "إدارة المخزون"],
        "company": "شركة الشحن السريع"
    },
    {
        "name": "نورا أحمد البقمي",
        "email": "nora.albaqami@retail.sa",
        "phone": "00966506789012",
        "language": "ar",
        "business_domain": "التجزئة",
        "challenges": ["تحليل سلوك العملاء", "إدارة المخزون", "التسويق الذكي"],
        "company": "مجموعة التجزئة الحديثة"
    }
]

WORKFLOW_TEMPLATES = [
    {
        "template_id": "email_automation",
        "name": "أتمتة البريد الإلكتروني",
        "description": "نظام آلي للرد على استفسارات العملاء",
        "complexity": "medium",
        "estimated_time": "15 minutes"
    },
    {
        "template_id": "data_processing",
        "name": "معالجة البيانات",
        "description": "تنظيف وتحليل البيانات تلقائياً",
        "complexity": "high",
        "estimated_time": "25 minutes"
    },
    {
        "template_id": "notifications",
        "name": "إشعارات تلقائية",
        "description": "إرسال إشعارات بناءً على أحداث معينة",
        "complexity": "low",
        "estimated_time": "10 minutes"
    },
    {
        "template_id": "system_integration",
        "name": "تكامل الأنظمة",
        "description": "ربط أنظمة مختلفة وتبادل البيانات",
        "complexity": "high",
        "estimated_time": "35 minutes"
    },
    {
        "template_id": "sentiment_analysis",
        "name": "تحليل المشاعر",
        "description": "تحليل مشاعر العملاء من التعليقات والمراجعات",
        "complexity": "medium",
        "estimated_time": "20 minutes"
    }
]

PROJECT_TYPES = [
    {
        "type": "chatbot_development",
        "name": "تطوير روبوت محادثة",
        "framework": "google_adk",
        "complexity": "medium",
        "timeline": "2-3 weeks"
    },
    {
        "type": "workflow_automation",
        "name": "أتمتة سير العمل",
        "framework": "langgraph",
        "complexity": "high",
        "timeline": "4-6 weeks"
    },
    {
        "type": "data_analysis_agent",
        "name": "وكيل تحليل البيانات",
        "framework": "pydantic",
        "complexity": "medium",
        "timeline": "3-4 weeks"
    },
    {
        "type": "customer_service_agent",
        "name": "وكيل خدمة العملاء",
        "framework": "google_adk",
        "complexity": "low",
        "timeline": "1-2 weeks"
    },
    {
        "type": "multi_agent_system",
        "name": "نظام متعدد الوكلاء",
        "framework": "langgraph",
        "complexity": "high",
        "timeline": "6-8 weeks"
    }
]

CONSULTATION_TYPES = [
    {
        "type": "ai_strategy",
        "name": "استشارة استراتيجية الذكاء الاصطناعي",
        "duration": "2-3 hours",
        "price": "3000-5000 SAR"
    },
    {
        "type": "feasibility_study",
        "name": "دراسة جدوى الذكاء الاصطناعي",
        "duration": "1-2 weeks",
        "price": "5000-8000 SAR"
    },
    {
        "type": "implementation_support",
        "name": "دعم التنفيذ",
        "duration": "Ongoing",
        "price": "2000-3000 SAR/month"
    },
    {
        "type": "quick_consultation",
        "name": "استشارة سريعة",
        "duration": "30-60 minutes",
        "price": "500-1000 SAR"
    }
]

class DemoDataGenerator:
    """Generate comprehensive demo data for all agents"""
    
    def __init__(self):
        self.customers = []
        self.workflows = []
        self.projects = []
        self.consultations = []
        self.workflow_executions = []
        self.consultation_sessions = []
    
    def generate_all_demo_data(self) -> Dict[str, Any]:
        """Generate complete demo dataset"""
        
        # Generate customers
        self._generate_customers()
        
        # Generate workflows for some customers
        self._generate_workflows()
        
        # Generate projects for some customers
        self._generate_projects()
        
        # Generate consultations for some customers
        self._generate_consultations()
        
        # Generate workflow executions
        self._generate_workflow_executions()
        
        # Generate consultation sessions
        self._generate_consultation_sessions()
        
        return {
            "customers": self.customers,
            "workflows": self.workflows,
            "projects": self.projects,
            "consultations": self.consultations,
            "workflow_executions": self.workflow_executions,
            "consultation_sessions": self.consultation_sessions,
            "summary": {
                "total_customers": len(self.customers),
                "total_workflows": len(self.workflows),
                "total_projects": len(self.projects),
                "total_consultations": len(self.consultations),
                "total_executions": len(self.workflow_executions),
                "total_sessions": len(self.consultation_sessions)
            }
        }
    
    def _generate_customers(self):
        """Generate sample customers"""
        for customer_data in SAMPLE_CUSTOMERS:
            customer = {
                "id": str(uuid.uuid4()),
                "name": customer_data["name"],
                "email": customer_data["email"],
                "phone": customer_data["phone"],
                "language": customer_data["language"],
                "source": random.choice(["website", "referral", "social_media", "direct"]),
                "status": random.choice(["new", "contacted", "qualified", "authenticated"]),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "notes": f"Customer interested in {customer_data['business_domain']} solutions",
                "metadata": {
                    "business_domain": customer_data["business_domain"],
                    "challenges": customer_data["challenges"],
                    "company": customer_data["company"],
                    "lead_score": random.randint(60, 95)
                }
            }
            self.customers.append(customer)
    
    def _generate_workflows(self):
        """Generate sample workflows"""
        # Create workflows for 70% of customers
        workflow_customers = random.sample(self.customers, int(len(self.customers) * 0.7))
        
        for customer in workflow_customers:
            # Each customer gets 1-3 workflows
            num_workflows = random.randint(1, 3)
            
            for _ in range(num_workflows):
                template = random.choice(WORKFLOW_TEMPLATES)
                
                workflow = {
                    "id": str(uuid.uuid4()),
                    "customer_id": customer["id"],
                    "n8n_workflow_id": f"n8n_{random.randint(1000, 9999)}",
                    "template_id": template["template_id"],
                    "name": f"{template['name']} - {customer['name'].split()[0]}",
                    "description": template["description"],
                    "status": random.choice(["created", "active", "paused", "completed"]),
                    "config": {
                        "template_id": template["template_id"],
                        "custom_settings": {
                            "frequency": random.choice(["hourly", "daily", "weekly"]),
                            "notifications": True,
                            "auto_retry": True
                        }
                    },
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                    "updated_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    "last_executed_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                    "execution_count": random.randint(5, 100),
                    "success_count": random.randint(4, 95),
                    "failure_count": random.randint(0, 5),
                    "metadata": {
                        "complexity": template["complexity"],
                        "estimated_time": template["estimated_time"],
                        "business_impact": random.choice(["high", "medium", "low"])
                    }
                }
                self.workflows.append(workflow)
    
    def _generate_projects(self):
        """Generate sample code generation projects"""
        # Create projects for 50% of customers
        project_customers = random.sample(self.customers, int(len(self.customers) * 0.5))
        
        for customer in project_customers:
            # Each customer gets 1-2 projects
            num_projects = random.randint(1, 2)
            
            for _ in range(num_projects):
                project_type = random.choice(PROJECT_TYPES)
                
                project = {
                    "id": str(uuid.uuid4()),
                    "customer_id": customer["id"],
                    "name": f"{project_type['name']} - {customer['metadata']['company']}",
                    "description": f"Custom {project_type['name']} for {customer['metadata']['business_domain']}",
                    "framework": project_type["framework"],
                    "complexity": project_type["complexity"],
                    "requirements": {
                        "agent_type": project_type["type"],
                        "functionalities": customer["metadata"]["challenges"][:3],
                        "data_sources": ["database", "api", "files"],
                        "integrations": ["supabase", "n8n", "livekit"],
                        "technical_requirements": ["python", "docker", "api"]
                    },
                    "architecture": {
                        "components": ["main_agent", "database", "api_layer"],
                        "deployment": "docker",
                        "monitoring": "prometheus"
                    },
                    "status": random.choice(["created", "in_progress", "completed", "deployed"]),
                    "estimated_timeline": project_type["timeline"],
                    "actual_timeline": project_type["timeline"] if random.choice([True, False]) else None,
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat(),
                    "updated_at": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat(),
                    "completed_at": (datetime.now() - timedelta(days=random.randint(0, 10))).isoformat() if random.choice([True, False]) else None,
                    "metadata": {
                        "code_files_count": random.randint(10, 50),
                        "test_files_count": random.randint(5, 25),
                        "documentation_files": random.randint(3, 10),
                        "estimated_cost": f"{random.randint(5000, 25000)} SAR"
                    }
                }
                self.projects.append(project)
    
    def _generate_consultations(self):
        """Generate sample consultations"""
        # Create consultations for 60% of customers
        consultation_customers = random.sample(self.customers, int(len(self.customers) * 0.6))
        
        for customer in consultation_customers:
            consultation_type = random.choice(CONSULTATION_TYPES)
            
            consultation = {
                "id": str(uuid.uuid4()),
                "customer_id": customer["id"],
                "consultation_type": consultation_type["type"],
                "business_domain": customer["metadata"]["business_domain"],
                "challenges": customer["metadata"]["challenges"],
                "desired_outcomes": [
                    "تحسين الكفاءة التشغيلية",
                    "تقليل التكاليف",
                    "تحسين تجربة العملاء",
                    "زيادة الإيرادات"
                ][:random.randint(2, 4)],
                "budget_range": f"{random.randint(10, 100)}K SAR",
                "timeline": random.choice(["1-3 months", "3-6 months", "6-12 months"]),
                "technical_requirements": ["cloud_deployment", "api_integration", "mobile_support"],
                "language": customer["language"],
                "status": random.choice(["requested", "scheduled", "in_progress", "completed"]),
                "scheduled_time": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "ai_recommendations": [
                    "تطبيق نظام إدارة علاقات العملاء الذكي",
                    "أتمتة العمليات المتكررة",
                    "تطوير نظام تحليل البيانات",
                    "تنفيذ حلول الذكاء الاصطناعي التنبؤية"
                ][:random.randint(2, 4)],
                "proposed_solutions": [
                    {
                        "solution": "AI-Powered CRM System",
                        "description": "نظام إدارة علاقات عملاء ذكي",
                        "estimated_cost": f"{random.randint(15, 50)}K SAR",
                        "timeline": "3-4 months"
                    },
                    {
                        "solution": "Workflow Automation",
                        "description": "أتمتة سير العمل الأساسية",
                        "estimated_cost": f"{random.randint(10, 30)}K SAR",
                        "timeline": "2-3 months"
                    }
                ],
                "estimated_cost": consultation_type["price"],
                "estimated_timeline": consultation_type["duration"],
                "requires_human_consultant": random.choice([True, False]),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat(),
                "completed_at": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat() if random.choice([True, False]) else None,
                "metadata": {
                    "consultation_rating": random.randint(4, 5),
                    "follow_up_required": random.choice([True, False]),
                    "referral_potential": random.choice(["high", "medium", "low"])
                }
            }
            self.consultations.append(consultation)
    
    def _generate_workflow_executions(self):
        """Generate sample workflow executions"""
        for workflow in self.workflows:
            # Generate 3-10 executions per workflow
            num_executions = random.randint(3, 10)
            
            for i in range(num_executions):
                execution = {
                    "id": str(uuid.uuid4()),
                    "workflow_id": workflow["id"],
                    "n8n_execution_id": f"exec_{random.randint(10000, 99999)}",
                    "status": random.choice(["completed", "failed", "running"]),
                    "input_data": {
                        "trigger": "scheduled",
                        "data_count": random.randint(10, 1000)
                    },
                    "output_data": {
                        "processed_items": random.randint(8, 950),
                        "success_rate": random.uniform(0.85, 1.0)
                    } if random.choice([True, False]) else None,
                    "started_at": (datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))).isoformat(),
                    "completed_at": (datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))).isoformat(),
                    "duration_seconds": random.randint(30, 600),
                    "success": random.choice([True, False]),
                    "error_message": "Connection timeout" if random.choice([True, False]) else None,
                    "logs": [
                        "Workflow started successfully",
                        "Processing data batch 1",
                        "Data transformation completed",
                        "Workflow completed successfully"
                    ],
                    "metadata": {
                        "execution_mode": "automatic",
                        "resource_usage": {
                            "cpu_seconds": random.randint(10, 120),
                            "memory_mb": random.randint(50, 500)
                        }
                    }
                }
                self.workflow_executions.append(execution)
    
    def _generate_consultation_sessions(self):
        """Generate sample consultation sessions"""
        for consultation in self.consultations:
            if consultation["requires_human_consultant"] and random.choice([True, False]):
                session = {
                    "id": str(uuid.uuid4()),
                    "consultation_id": consultation["id"],
                    "customer_id": consultation["customer_id"],
                    "room_name": f"consultation_{consultation['id'][:8]}",
                    "room_url": f"https://livekit.consulting.sa/room/{consultation['id'][:8]}",
                    "status": random.choice(["scheduled", "in_progress", "completed"]),
                    "language": consultation["language"],
                    "started_at": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat(),
                    "ended_at": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat(),
                    "duration_minutes": random.randint(30, 120),
                    "participants": ["customer", "consultant"],
                    "recording_url": f"https://recordings.consulting.sa/{consultation['id']}.mp4" if random.choice([True, False]) else None,
                    "transcript": "Session transcript would be here..." if random.choice([True, False]) else None,
                    "notes": "Customer showed strong interest in AI automation solutions. Follow-up scheduled.",
                    "follow_up_required": random.choice([True, False]),
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat(),
                    "metadata": {
                        "session_quality": random.choice(["excellent", "good", "fair"]),
                        "customer_satisfaction": random.randint(4, 5),
                        "technical_issues": random.choice([True, False])
                    }
                }
                self.consultation_sessions.append(session)
    
    def save_to_file(self, filename: str = "demo_data.json"):
        """Save generated data to JSON file"""
        data = self.generate_all_demo_data()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Demo data saved to {filename}")
        print(f"Generated {data['summary']['total_customers']} customers")
        print(f"Generated {data['summary']['total_workflows']} workflows")
        print(f"Generated {data['summary']['total_projects']} projects")
        print(f"Generated {data['summary']['total_consultations']} consultations")
        print(f"Generated {data['summary']['total_executions']} workflow executions")
        print(f"Generated {data['summary']['total_sessions']} consultation sessions")
        
        return data

def main():
    """Generate and save demo data"""
    generator = DemoDataGenerator()
    data = generator.save_to_file("agent/demo_data.json")
    
    # Print some sample data
    print("\n=== Sample Customer ===")
    print(json.dumps(data["customers"][0], ensure_ascii=False, indent=2))
    
    print("\n=== Sample Workflow ===")
    if data["workflows"]:
        print(json.dumps(data["workflows"][0], ensure_ascii=False, indent=2))
    
    print("\n=== Sample Project ===")
    if data["projects"]:
        print(json.dumps(data["projects"][0], ensure_ascii=False, indent=2))
    
    print("\n=== Sample Consultation ===")
    if data["consultations"]:
        print(json.dumps(data["consultations"][0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()