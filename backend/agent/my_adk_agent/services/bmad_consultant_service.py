"""BMAD Consultant Service - Integrates BMAD methodology into consulting agent."""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class BMADConsultantService:
    """Service for BMAD methodology integration in consulting."""
    
    def __init__(self):
        """Initialize BMAD consultant service."""
        self.bmad_templates_path = os.path.join(os.path.dirname(__file__), "../../../BMAD-METHOD")
        self.project_templates = self._load_bmad_templates()
        logger.info("BMAD Consultant Service initialized")
    
    def _load_bmad_templates(self) -> Dict[str, Any]:
        """Load BMAD templates and methodology."""
        templates = {
            "planning_agents": {
                "analyst": "Analyzes requirements and creates detailed briefs",
                "pm": "Manages project scope and creates structured plans", 
                "architect": "Designs system architecture and technical specifications"
            },
            "development_workflow": {
                "context_engineering": "Embeds full context in development stories",
                "story_generation": "Creates hyper-detailed development stories",
                "human_in_loop": "Maintains human oversight and refinement"
            },
            "document_types": {
                "prd": "Product Requirements Document",
                "architecture": "System Architecture Document", 
                "stories": "Context-Engineered Development Stories"
            }
        }
        return templates
    
    async def create_project_requirements(self, brief: str, customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create PRD using BMAD agentic planning methodology."""
        try:
            # Analyst phase - analyze requirements
            analysis = await self._analyze_requirements(brief, customer_context)
            
            # PM phase - structure requirements
            structured_requirements = await self._structure_requirements(analysis)
            
            # Create PRD document
            prd = {
                "title": f"PRD - {customer_context.get('project_name', 'Customer Project')}",
                "created_at": datetime.now().isoformat(),
                "customer_context": customer_context,
                "analysis": analysis,
                "requirements": structured_requirements,
                "methodology": "BMAD Agentic Planning"
            }
            
            return prd
            
        except Exception as e:
            logger.error(f"Error creating project requirements: {e}")
            raise  
  
    async def _analyze_requirements(self, brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements using BMAD analyst methodology."""
        analysis = {
            "brief_analysis": {
                "original_brief": brief,
                "key_requirements": self._extract_key_requirements(brief),
                "business_goals": self._identify_business_goals(brief),
                "technical_constraints": self._identify_constraints(brief, context),
                "success_criteria": self._define_success_criteria(brief)
            },
            "stakeholder_analysis": {
                "primary_stakeholders": context.get("stakeholders", []),
                "user_personas": self._create_user_personas(brief, context),
                "business_impact": self._assess_business_impact(brief, context)
            },
            "scope_definition": {
                "in_scope": self._define_in_scope(brief),
                "out_of_scope": self._define_out_of_scope(brief),
                "assumptions": self._list_assumptions(brief, context),
                "dependencies": self._identify_dependencies(brief, context)
            }
        }
        return analysis
    
    async def _structure_requirements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Structure requirements using BMAD PM methodology."""
        structured = {
            "functional_requirements": self._create_functional_requirements(analysis),
            "non_functional_requirements": self._create_non_functional_requirements(analysis),
            "user_stories": self._create_user_stories(analysis),
            "acceptance_criteria": self._create_acceptance_criteria(analysis),
            "priority_matrix": self._create_priority_matrix(analysis),
            "timeline_estimate": self._estimate_timeline(analysis)
        }
        return structured
    
    async def design_architecture(self, prd: Dict[str, Any]) -> Dict[str, Any]:
        """Design system architecture using BMAD methodology."""
        try:
            # Architect phase - design system
            architecture = {
                "title": f"Architecture - {prd.get('title', 'System')}",
                "created_at": datetime.now().isoformat(),
                "based_on_prd": prd.get("title"),
                "system_overview": self._create_system_overview(prd),
                "technical_architecture": self._design_technical_architecture(prd),
                "data_architecture": self._design_data_architecture(prd),
                "integration_architecture": self._design_integration_architecture(prd),
                "security_architecture": self._design_security_architecture(prd),
                "deployment_architecture": self._design_deployment_architecture(prd),
                "methodology": "BMAD Context-Engineered Architecture"
            }
            
            return architecture
            
        except Exception as e:
            logger.error(f"Error designing architecture: {e}")
            raise
    
    async def generate_development_stories(self, architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate context-engineered development stories."""
        try:
            stories = []
            
            # Generate stories for each architectural component
            components = architecture.get("technical_architecture", {}).get("components", [])
            
            for component in components:
                component_stories = self._create_component_stories(component, architecture)
                stories.extend(component_stories)
            
            # Add integration stories
            integration_stories = self._create_integration_stories(architecture)
            stories.extend(integration_stories)
            
            # Add testing stories
            testing_stories = self._create_testing_stories(architecture)
            stories.extend(testing_stories)
            
            # Add deployment stories
            deployment_stories = self._create_deployment_stories(architecture)
            stories.extend(deployment_stories)
            
            return stories
            
        except Exception as e:
            logger.error(f"Error generating development stories: {e}")
            raise
    
    def _extract_key_requirements(self, brief: str) -> List[str]:
        """Extract key requirements from brief."""
        # Simple keyword-based extraction (would use LLM in production)
        keywords = ["need", "want", "require", "must", "should", "feature", "function"]
        sentences = brief.split('.')
        requirements = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                requirements.append(sentence.strip())
        
        return requirements[:10]  # Limit to top 10
    
    def _identify_business_goals(self, brief: str) -> List[str]:
        """Identify business goals from brief."""
        business_keywords = ["revenue", "cost", "efficiency", "customer", "market", "growth", "profit"]
        goals = []
        
        for keyword in business_keywords:
            if keyword in brief.lower():
                goals.append(f"Improve {keyword} through solution implementation")
        
        if not goals:
            goals.append("Achieve business objectives through technology solution")
        
        return goals
    
    def _create_user_personas(self, brief: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create user personas based on brief and context."""
        personas = [
            {
                "name": "Primary User",
                "role": context.get("primary_user_role", "End User"),
                "goals": ["Accomplish tasks efficiently", "Have positive user experience"],
                "pain_points": ["Current system limitations", "Manual processes"],
                "technical_level": "Medium"
            }
        ]
        
        if "admin" in brief.lower() or "manage" in brief.lower():
            personas.append({
                "name": "System Administrator",
                "role": "Admin User",
                "goals": ["Manage system effectively", "Monitor performance"],
                "pain_points": ["Complex administration", "Limited visibility"],
                "technical_level": "High"
            })
        
        return personas
    
    def _create_functional_requirements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create functional requirements from analysis."""
        requirements = []
        key_reqs = analysis.get("brief_analysis", {}).get("key_requirements", [])
        
        for i, req in enumerate(key_reqs, 1):
            requirements.append({
                "id": f"FR-{i:03d}",
                "title": f"Functional Requirement {i}",
                "description": req,
                "priority": "High" if i <= 3 else "Medium",
                "complexity": "Medium",
                "dependencies": []
            })
        
        return requirements
    
    def _create_user_stories(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create user stories from analysis."""
        stories = []
        personas = analysis.get("stakeholder_analysis", {}).get("user_personas", [])
        requirements = analysis.get("brief_analysis", {}).get("key_requirements", [])
        
        for i, req in enumerate(requirements[:5], 1):  # Limit to 5 main stories
            persona = personas[0] if personas else {"name": "User", "role": "User"}
            
            stories.append({
                "id": f"US-{i:03d}",
                "title": f"User Story {i}",
                "story": f"As a {persona['role']}, I want to {req.lower()}, so that I can achieve my goals efficiently",
                "acceptance_criteria": [
                    f"Given the user is authenticated",
                    f"When they {req.lower()}",
                    f"Then the system should respond appropriately"
                ],
                "priority": "High" if i <= 2 else "Medium",
                "story_points": 5 if i <= 2 else 3
            })
        
        return stories
    
    def _create_component_stories(self, component: Dict[str, Any], architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create development stories for a component."""
        component_name = component.get("name", "Component")
        stories = []
        
        # Setup story
        stories.append({
            "id": f"DEV-{component_name}-001",
            "title": f"Setup {component_name} Foundation",
            "description": f"Create the foundational structure for {component_name}",
            "context": {
                "component": component,
                "architecture_reference": architecture.get("title"),
                "dependencies": component.get("dependencies", []),
                "interfaces": component.get("interfaces", [])
            },
            "tasks": [
                f"Create {component_name} directory structure",
                f"Setup {component_name} configuration",
                f"Implement basic {component_name} interface",
                f"Add {component_name} tests"
            ],
            "definition_of_done": [
                f"{component_name} structure is created",
                f"Basic functionality is implemented",
                f"Tests are passing",
                f"Code review is completed"
            ]
        })
        
        # Implementation story
        stories.append({
            "id": f"DEV-{component_name}-002", 
            "title": f"Implement {component_name} Core Logic",
            "description": f"Implement the core business logic for {component_name}",
            "context": {
                "component": component,
                "business_rules": component.get("business_rules", []),
                "data_models": component.get("data_models", []),
                "validation_rules": component.get("validation_rules", [])
            },
            "tasks": [
                f"Implement {component_name} business logic",
                f"Add data validation",
                f"Implement error handling",
                f"Add comprehensive tests"
            ],
            "definition_of_done": [
                f"Core logic is implemented",
                f"All business rules are enforced",
                f"Error handling is comprehensive",
                f"Test coverage is > 80%"
            ]
        })
        
        return stories
    
    def _create_system_overview(self, prd: Dict[str, Any]) -> Dict[str, Any]:
        """Create system overview from PRD."""
        return {
            "purpose": "System designed to meet customer requirements",
            "scope": prd.get("requirements", {}).get("functional_requirements", []),
            "key_features": [req.get("title", "") for req in prd.get("requirements", {}).get("functional_requirements", [])[:5]],
            "target_users": [persona.get("name", "") for persona in prd.get("analysis", {}).get("stakeholder_analysis", {}).get("user_personas", [])],
            "success_metrics": prd.get("analysis", {}).get("brief_analysis", {}).get("success_criteria", [])
        }
    
    def _design_technical_architecture(self, prd: Dict[str, Any]) -> Dict[str, Any]:
        """Design technical architecture from PRD."""
        return {
            "architecture_pattern": "Microservices",
            "components": [
                {
                    "name": "Frontend",
                    "type": "User Interface",
                    "technology": "React/Next.js",
                    "responsibilities": ["User interaction", "Data presentation"],
                    "interfaces": ["Backend API"],
                    "dependencies": ["Backend Service"]
                },
                {
                    "name": "Backend",
                    "type": "API Service", 
                    "technology": "Python/FastAPI",
                    "responsibilities": ["Business logic", "Data processing"],
                    "interfaces": ["REST API", "Database"],
                    "dependencies": ["Database", "External APIs"]
                },
                {
                    "name": "Database",
                    "type": "Data Storage",
                    "technology": "PostgreSQL",
                    "responsibilities": ["Data persistence", "Data integrity"],
                    "interfaces": ["SQL Interface"],
                    "dependencies": []
                }
            ],
            "integration_patterns": ["REST API", "Event-driven"],
            "scalability_approach": "Horizontal scaling",
            "performance_targets": {
                "response_time": "< 500ms",
                "throughput": "1000 requests/second",
                "availability": "99.9%"
            }
        }
    
    async def manage_project_workflow(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Manage project using BMAD workflow."""
        try:
            workflow_status = {
                "project_id": project.get("id"),
                "current_phase": self._determine_current_phase(project),
                "completed_phases": project.get("completed_phases", []),
                "next_actions": self._determine_next_actions(project),
                "blockers": self._identify_blockers(project),
                "progress_percentage": self._calculate_progress(project),
                "estimated_completion": self._estimate_completion(project),
                "methodology": "BMAD Workflow Management"
            }
            
            return workflow_status
            
        except Exception as e:
            logger.error(f"Error managing project workflow: {e}")
            raise
    
    def _determine_current_phase(self, project: Dict[str, Any]) -> str:
        """Determine current project phase."""
        if not project.get("prd_completed"):
            return "Requirements Analysis"
        elif not project.get("architecture_completed"):
            return "Architecture Design"
        elif not project.get("stories_generated"):
            return "Story Generation"
        elif not project.get("development_started"):
            return "Development Planning"
        elif not project.get("development_completed"):
            return "Development"
        elif not project.get("testing_completed"):
            return "Testing"
        else:
            return "Deployment"
    
    def _determine_next_actions(self, project: Dict[str, Any]) -> List[str]:
        """Determine next actions for project."""
        current_phase = self._determine_current_phase(project)
        
        actions_map = {
            "Requirements Analysis": [
                "Complete stakeholder interviews",
                "Finalize PRD document",
                "Get PRD approval"
            ],
            "Architecture Design": [
                "Design system architecture",
                "Create technical specifications",
                "Review architecture with team"
            ],
            "Story Generation": [
                "Generate development stories",
                "Add context to stories",
                "Prioritize story backlog"
            ],
            "Development Planning": [
                "Plan development sprints",
                "Assign stories to developers",
                "Setup development environment"
            ],
            "Development": [
                "Implement features",
                "Conduct code reviews",
                "Update progress tracking"
            ],
            "Testing": [
                "Execute test plans",
                "Fix identified issues",
                "Validate acceptance criteria"
            ],
            "Deployment": [
                "Prepare deployment",
                "Execute deployment plan",
                "Monitor system performance"
            ]
        }
        
        return actions_map.get(current_phase, ["Continue current phase activities"])
    
    def _calculate_progress(self, project: Dict[str, Any]) -> float:
        """Calculate project progress percentage."""
        phases = [
            "prd_completed",
            "architecture_completed", 
            "stories_generated",
            "development_started",
            "development_completed",
            "testing_completed",
            "deployment_completed"
        ]
        
        completed = sum(1 for phase in phases if project.get(phase, False))
        return (completed / len(phases)) * 100