"""
Code Generation Agent - LangGraph Framework
Handles medium complexity requests for building custom agentic workflows with code
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, TypedDict, Annotated
import logging

# Import LangGraph components with fallback
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.tools import BaseTool
    from langchain.schema import HumanMessage, AIMessage
except ImportError:
    # Mock implementations for development
    class StateGraph:
        def __init__(self, state_type): pass
        def add_node(self, name, func): pass
        def set_entry_point(self, name): pass
        def add_edge(self, from_node, to_node): pass
        def compile(self): return MockWorkflow()
    
    class MockWorkflow:
        async def ainvoke(self, state): return state
    
    END = "END"
    ToolExecutor = None
    
    class ChatGoogleGenerativeAI:
        def __init__(self, **kwargs): pass
        async def ainvoke(self, messages): 
            return type('MockResponse', (), {'content': 'Mock response'})()
    
    BaseTool = object
    HumanMessage = lambda content: {"content": content}
    AIMessage = lambda content: {"content": content}

from ..services.supabase_service import SupabaseService
from ..models.project import Project, CodeGeneration

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the code generation agent"""
    messages: List[Dict[str, Any]]
    customer_id: str
    project_id: Optional[str]
    requirements: Dict[str, Any]
    generated_code: Dict[str, Any]
    current_step: str
    language: str
    framework: str
    complexity: str
    next_action: str

class CodeGenerationAgent:
    """
    Code generation agent using LangGraph framework
    - Analyzes customer requirements for agentic workflows
    - Generates code using Google ADK, LangGraph, or Pydantic
    - Provides step-by-step implementation guidance
    - Creates complete project structures
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supabase = SupabaseService(config)
        
        # Initialize LangGraph components
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=config.get("GOOGLE_API_KEY"),
            temperature=0.3
        )
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
        
        # Available frameworks and their capabilities
        self.frameworks = {
            "google_adk": {
                "name": "Google ADK",
                "name_ar": "جوجل ADK",
                "description": "Google Agent Development Kit for production-ready agents",
                "description_ar": "مجموعة تطوير الوكلاء من جوجل للوكلاء الجاهزة للإنتاج",
                "best_for": ["simple_agents", "production_deployment", "google_integration"],
                "complexity": "low_to_medium",
                "languages": ["python"],
                "features": ["built_in_tools", "web_ui", "evaluation_framework"]
            },
            "langgraph": {
                "name": "LangGraph",
                "name_ar": "لانج جراف",
                "description": "Advanced framework for complex multi-agent workflows",
                "description_ar": "إطار عمل متقدم لسير العمل المعقد متعدد الوكلاء",
                "best_for": ["complex_workflows", "multi_agent_systems", "state_management"],
                "complexity": "medium_to_high",
                "languages": ["python"],
                "features": ["state_graphs", "conditional_routing", "human_in_loop"]
            },
            "pydantic": {
                "name": "Pydantic AI",
                "name_ar": "بايدانتيك AI",
                "description": "Simple and elegant framework for structured AI applications",
                "description_ar": "إطار عمل بسيط وأنيق للتطبيقات المنظمة للذكاء الاصطناعي",
                "best_for": ["data_validation", "structured_output", "simple_workflows"],
                "complexity": "low",
                "languages": ["python"],
                "features": ["type_safety", "data_validation", "easy_integration"]
            }
        }
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for code generation"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("select_framework", self._select_framework)
        workflow.add_node("generate_architecture", self._generate_architecture)
        workflow.add_node("generate_code", self._generate_code)
        workflow.add_node("create_tests", self._create_tests)
        workflow.add_node("generate_documentation", self._generate_documentation)
        workflow.add_node("finalize_project", self._finalize_project)
        
        # Set entry point
        workflow.set_entry_point("analyze_requirements")
        
        # Add edges
        workflow.add_edge("analyze_requirements", "select_framework")
        workflow.add_edge("select_framework", "generate_architecture")
        workflow.add_edge("generate_architecture", "generate_code")
        workflow.add_edge("generate_code", "create_tests")
        workflow.add_edge("create_tests", "generate_documentation")
        workflow.add_edge("generate_documentation", "finalize_project")
        workflow.add_edge("finalize_project", END)
        
        return workflow.compile()
    
    async def _analyze_requirements(self, state: AgentState) -> AgentState:
        """Analyze customer requirements and extract key information"""
        try:
            messages = state["messages"]
            language = state["language"]
            
            # Create analysis prompt
            analysis_prompt = f"""
            تحليل متطلبات العميل لبناء وكيل ذكي / Analyze customer requirements for building an AI agent
            
            الرسائل / Messages: {json.dumps(messages, ensure_ascii=False)}
            
            استخرج المعلومات التالية / Extract the following information:
            1. نوع الوكيل المطلوب / Type of agent needed
            2. الوظائف الأساسية / Core functionalities
            3. مصادر البيانات / Data sources
            4. التكاملات المطلوبة / Required integrations
            5. مستوى التعقيد / Complexity level
            6. المتطلبات الفنية / Technical requirements
            
            أجب بصيغة JSON / Respond in JSON format:
            {{
                "agent_type": "نوع الوكيل",
                "functionalities": ["وظيفة 1", "وظيفة 2"],
                "data_sources": ["مصدر 1", "مصدر 2"],
                "integrations": ["تكامل 1", "تكامل 2"],
                "complexity": "low|medium|high",
                "technical_requirements": ["متطلب 1", "متطلب 2"],
                "estimated_timeline": "المدة المتوقعة",
                "recommended_framework": "الإطار المقترح"
            }}
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            # Parse the JSON response
            try:
                requirements = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback to basic requirements
                requirements = {
                    "agent_type": "general_purpose",
                    "functionalities": ["basic_chat", "information_retrieval"],
                    "data_sources": ["database"],
                    "integrations": ["api"],
                    "complexity": "medium",
                    "technical_requirements": ["python", "database"],
                    "estimated_timeline": "2-3 weeks",
                    "recommended_framework": "google_adk"
                }
            
            state["requirements"] = requirements
            state["complexity"] = requirements["complexity"]
            state["current_step"] = "requirements_analyzed"
            
            logger.info(f"Requirements analyzed for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {e}")
            state["current_step"] = "error"
            return state
    
    async def _select_framework(self, state: AgentState) -> AgentState:
        """Select the best framework based on requirements"""
        try:
            requirements = state["requirements"]
            complexity = requirements["complexity"]
            functionalities = requirements.get("functionalities", [])
            
            # Framework selection logic
            if complexity == "low" or "simple" in str(functionalities).lower():
                selected_framework = "pydantic"
            elif complexity == "high" or any(keyword in str(functionalities).lower() 
                                           for keyword in ["multi_agent", "complex", "workflow"]):
                selected_framework = "langgraph"
            else:
                selected_framework = "google_adk"
            
            # Override with recommended framework if specified
            if requirements.get("recommended_framework") in self.frameworks:
                selected_framework = requirements["recommended_framework"]
            
            state["framework"] = selected_framework
            state["current_step"] = "framework_selected"
            
            logger.info(f"Framework selected: {selected_framework} for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error selecting framework: {e}")
            state["current_step"] = "error"
            return state
    
    async def _generate_architecture(self, state: AgentState) -> AgentState:
        """Generate system architecture and project structure"""
        try:
            requirements = state["requirements"]
            framework = state["framework"]
            language = state["language"]
            
            framework_info = self.frameworks[framework]
            
            architecture_prompt = f"""
            إنشاء هيكل المشروع والمعمارية / Generate project architecture and structure
            
            المتطلبات / Requirements: {json.dumps(requirements, ensure_ascii=False)}
            الإطار المختار / Selected Framework: {framework_info['name']}
            
            أنشئ هيكل مشروع مفصل يتضمن / Create detailed project structure including:
            1. هيكل المجلدات والملفات / Folder and file structure
            2. المكونات الأساسية / Core components
            3. نقاط التكامل / Integration points
            4. قاعدة البيانات / Database schema
            5. واجهات البرمجة / API endpoints
            6. اختبارات / Tests
            7. وثائق / Documentation
            
            أجب بصيغة JSON / Respond in JSON format:
            {{
                "project_structure": {{
                    "folders": ["مجلد 1", "مجلد 2"],
                    "files": ["ملف 1", "ملف 2"]
                }},
                "components": [
                    {{
                        "name": "اسم المكون",
                        "description": "وصف المكون",
                        "file_path": "مسار الملف"
                    }}
                ],
                "database_schema": {{
                    "tables": ["جدول 1", "جدول 2"]
                }},
                "api_endpoints": [
                    {{
                        "method": "GET|POST",
                        "path": "/api/endpoint",
                        "description": "وصف النقطة"
                    }}
                ],
                "dependencies": ["مكتبة 1", "مكتبة 2"],
                "environment_variables": ["متغير 1", "متغير 2"]
            }}
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=architecture_prompt)])
            
            try:
                architecture = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback architecture
                architecture = {
                    "project_structure": {
                        "folders": ["src", "tests", "docs", "config"],
                        "files": ["main.py", "requirements.txt", "README.md"]
                    },
                    "components": [
                        {
                            "name": "Main Agent",
                            "description": "Primary agent component",
                            "file_path": "src/agent.py"
                        }
                    ],
                    "database_schema": {
                        "tables": ["customers", "conversations", "logs"]
                    },
                    "api_endpoints": [
                        {
                            "method": "POST",
                            "path": "/api/chat",
                            "description": "Chat endpoint"
                        }
                    ],
                    "dependencies": ["google-adk", "supabase", "fastapi"],
                    "environment_variables": ["GOOGLE_API_KEY", "SUPABASE_URL"]
                }
            
            state["generated_code"] = {"architecture": architecture}
            state["current_step"] = "architecture_generated"
            
            logger.info(f"Architecture generated for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating architecture: {e}")
            state["current_step"] = "error"
            return state
    
    async def _generate_code(self, state: AgentState) -> AgentState:
        """Generate the actual code implementation"""
        try:
            requirements = state["requirements"]
            framework = state["framework"]
            architecture = state["generated_code"]["architecture"]
            language = state["language"]
            
            # Generate code for each component
            generated_files = {}
            
            for component in architecture["components"]:
                code_prompt = f"""
                إنشاء كود للمكون / Generate code for component: {component['name']}
                
                الوصف / Description: {component['description']}
                الإطار / Framework: {framework}
                المتطلبات / Requirements: {json.dumps(requirements, ensure_ascii=False)}
                
                أنشئ كود Python كامل وجاهز للتشغيل / Generate complete, runnable Python code
                يجب أن يتضمن / Must include:
                1. الاستيرادات المطلوبة / Required imports
                2. التوثيق والتعليقات / Documentation and comments
                3. معالجة الأخطاء / Error handling
                4. أفضل الممارسات / Best practices
                5. دعم اللغة العربية / Arabic language support
                """
                
                response = await self.llm.ainvoke([HumanMessage(content=code_prompt)])
                
                # Clean up the code response
                code_content = response.content
                if "```python" in code_content:
                    code_content = code_content.split("```python")[1].split("```")[0].strip()
                elif "```" in code_content:
                    code_content = code_content.split("```")[1].split("```")[0].strip()
                
                generated_files[component["file_path"]] = code_content
            
            # Generate additional files
            additional_files = {
                "requirements.txt": self._generate_requirements(framework, architecture["dependencies"]),
                "README.md": self._generate_readme(requirements, framework, language),
                ".env.example": self._generate_env_example(architecture["environment_variables"]),
                "config.py": self._generate_config_file(framework),
                "main.py": self._generate_main_file(framework, requirements)
            }
            
            generated_files.update(additional_files)
            
            state["generated_code"]["files"] = generated_files
            state["current_step"] = "code_generated"
            
            logger.info(f"Code generated for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            state["current_step"] = "error"
            return state
    
    async def _create_tests(self, state: AgentState) -> AgentState:
        """Generate test files for the project"""
        try:
            requirements = state["requirements"]
            framework = state["framework"]
            generated_files = state["generated_code"]["files"]
            
            test_files = {}
            
            # Generate test for main components
            for file_path, code_content in generated_files.items():
                if file_path.endswith(".py") and not file_path.startswith("test_"):
                    test_prompt = f"""
                    إنشاء اختبارات للكود / Generate tests for code:
                    
                    ملف / File: {file_path}
                    الكود / Code: {code_content[:1000]}...
                    
                    أنشئ اختبارات شاملة باستخدام pytest / Generate comprehensive tests using pytest:
                    1. اختبارات الوحدة / Unit tests
                    2. اختبارات التكامل / Integration tests
                    3. اختبارات الأخطاء / Error handling tests
                    4. اختبارات الأداء / Performance tests
                    """
                    
                    response = await self.llm.ainvoke([HumanMessage(content=test_prompt)])
                    
                    test_content = response.content
                    if "```python" in test_content:
                        test_content = test_content.split("```python")[1].split("```")[0].strip()
                    
                    test_file_name = f"tests/test_{file_path.split('/')[-1]}"
                    test_files[test_file_name] = test_content
            
            # Add pytest configuration
            test_files["pytest.ini"] = """
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
"""
            
            state["generated_code"]["test_files"] = test_files
            state["current_step"] = "tests_created"
            
            logger.info(f"Tests created for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error creating tests: {e}")
            state["current_step"] = "error"
            return state
    
    async def _generate_documentation(self, state: AgentState) -> AgentState:
        """Generate comprehensive documentation"""
        try:
            requirements = state["requirements"]
            framework = state["framework"]
            architecture = state["generated_code"]["architecture"]
            language = state["language"]
            
            # Generate documentation files
            doc_files = {}
            
            # API Documentation
            if architecture.get("api_endpoints"):
                api_doc_prompt = f"""
                إنشاء وثائق API / Generate API documentation
                
                النقاط / Endpoints: {json.dumps(architecture['api_endpoints'], ensure_ascii=False)}
                
                أنشئ وثائق API شاملة بصيغة Markdown / Generate comprehensive API docs in Markdown:
                1. نظرة عامة / Overview
                2. المصادقة / Authentication
                3. النقاط والمعاملات / Endpoints and parameters
                4. أمثلة الطلبات والردود / Request/response examples
                5. رموز الأخطاء / Error codes
                """
                
                response = await self.llm.ainvoke([HumanMessage(content=api_doc_prompt)])
                doc_files["docs/api.md"] = response.content
            
            # User Guide
            user_guide_prompt = f"""
            إنشاء دليل المستخدم / Generate user guide
            
            المتطلبات / Requirements: {json.dumps(requirements, ensure_ascii=False)}
            الإطار / Framework: {framework}
            
            أنشئ دليل مستخدم شامل / Generate comprehensive user guide:
            1. مقدمة / Introduction
            2. التثبيت / Installation
            3. الإعداد / Configuration
            4. الاستخدام / Usage
            5. أمثلة / Examples
            6. استكشاف الأخطاء / Troubleshooting
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=user_guide_prompt)])
            doc_files["docs/user_guide.md"] = response.content
            
            # Developer Guide
            dev_guide_prompt = f"""
            إنشاء دليل المطور / Generate developer guide
            
            الهيكل / Architecture: {json.dumps(architecture, ensure_ascii=False)}
            
            أنشئ دليل مطور تقني / Generate technical developer guide:
            1. هيكل المشروع / Project structure
            2. المعمارية / Architecture
            3. إضافة ميزات جديدة / Adding new features
            4. اختبار / Testing
            5. نشر / Deployment
            6. المساهمة / Contributing
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=dev_guide_prompt)])
            doc_files["docs/developer_guide.md"] = response.content
            
            state["generated_code"]["documentation"] = doc_files
            state["current_step"] = "documentation_generated"
            
            logger.info(f"Documentation generated for customer {state['customer_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            state["current_step"] = "error"
            return state
    
    async def _finalize_project(self, state: AgentState) -> AgentState:
        """Finalize the project and store in database"""
        try:
            customer_id = state["customer_id"]
            requirements = state["requirements"]
            framework = state["framework"]
            generated_code = state["generated_code"]
            
            # Create project record in database
            project_data = {
                "customer_id": customer_id,
                "name": f"{requirements.get('agent_type', 'Custom Agent')} - {framework}",
                "description": f"Generated {framework} agent project",
                "framework": framework,
                "complexity": state["complexity"],
                "requirements": requirements,
                "architecture": generated_code.get("architecture", {}),
                "status": "completed",
                "estimated_timeline": requirements.get("estimated_timeline", "Unknown")
            }
            
            project = await self.supabase.create_project(project_data)
            
            # Store generated files
            for file_path, content in generated_code.get("files", {}).items():
                await self.supabase.create_code_file({
                    "project_id": project.id,
                    "file_path": file_path,
                    "content": content,
                    "file_type": "source"
                })
            
            # Store test files
            for file_path, content in generated_code.get("test_files", {}).items():
                await self.supabase.create_code_file({
                    "project_id": project.id,
                    "file_path": file_path,
                    "content": content,
                    "file_type": "test"
                })
            
            # Store documentation
            for file_path, content in generated_code.get("documentation", {}).items():
                await self.supabase.create_code_file({
                    "project_id": project.id,
                    "file_path": file_path,
                    "content": content,
                    "file_type": "documentation"
                })
            
            state["project_id"] = project.id
            state["current_step"] = "completed"
            state["next_action"] = "project_ready"
            
            logger.info(f"Project finalized: {project.id} for customer {customer_id}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error finalizing project: {e}")
            state["current_step"] = "error"
            return state
    
    def _generate_requirements(self, framework: str, dependencies: List[str]) -> str:
        """Generate requirements.txt content"""
        base_requirements = {
            "google_adk": [
                "google-adk>=1.0.0",
                "google-generativeai>=0.3.0",
                "supabase>=2.0.0",
                "fastapi>=0.104.0",
                "uvicorn>=0.24.0"
            ],
            "langgraph": [
                "langgraph>=0.0.40",
                "langchain>=0.1.0",
                "langchain-google-genai>=1.0.0",
                "supabase>=2.0.0",
                "fastapi>=0.104.0"
            ],
            "pydantic": [
                "pydantic-ai>=0.0.8",
                "pydantic>=2.5.0",
                "supabase>=2.0.0",
                "fastapi>=0.104.0"
            ]
        }
        
        requirements = base_requirements.get(framework, [])
        requirements.extend(dependencies)
        
        # Add common dependencies
        requirements.extend([
            "python-dotenv>=1.0.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0"
        ])
        
        return "\n".join(sorted(set(requirements)))
    
    def _generate_readme(self, requirements: Dict[str, Any], framework: str, language: str) -> str:
        """Generate README.md content"""
        if language == "ar":
            return f"""
# {requirements.get('agent_type', 'وكيل ذكي مخصص')}

## نظرة عامة
هذا المشروع تم إنشاؤه باستخدام {framework} لبناء وكيل ذكي متخصص.

## الميزات
{chr(10).join(f"- {feature}" for feature in requirements.get('functionalities', []))}

## التثبيت
```bash
pip install -r requirements.txt
```

## الإعداد
1. انسخ `.env.example` إلى `.env`
2. أضف مفاتيح API المطلوبة
3. قم بتشغيل قاعدة البيانات

## الاستخدام
```bash
python main.py
```

## الاختبار
```bash
pytest
```

## المساهمة
مرحب بالمساهمات! يرجى قراءة دليل المطور أولاً.

## الترخيص
MIT License
"""
        else:
            return f"""
# {requirements.get('agent_type', 'Custom AI Agent')}

## Overview
This project was generated using {framework} to build a specialized AI agent.

## Features
{chr(10).join(f"- {feature}" for feature in requirements.get('functionalities', []))}

## Installation
```bash
pip install -r requirements.txt
```

## Setup
1. Copy `.env.example` to `.env`
2. Add required API keys
3. Set up database

## Usage
```bash
python main.py
```

## Testing
```bash
pytest
```

## Contributing
Contributions are welcome! Please read the developer guide first.

## License
MIT License
"""
    
    def _generate_env_example(self, env_vars: List[str]) -> str:
        """Generate .env.example content"""
        env_content = []
        for var in env_vars:
            if "API_KEY" in var:
                env_content.append(f"{var}=your_api_key_here")
            elif "URL" in var:
                env_content.append(f"{var}=https://your-service-url.com")
            elif "SECRET" in var:
                env_content.append(f"{var}=your_secret_here")
            else:
                env_content.append(f"{var}=your_value_here")
        
        return "\n".join(env_content)
    
    def _generate_config_file(self, framework: str) -> str:
        """Generate configuration file"""
        return f"""
import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    \"\"\"Get application configuration\"\"\"
    return {{
        "framework": "{framework}",
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_ANON_KEY"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO")
    }}
"""
    
    def _generate_main_file(self, framework: str, requirements: Dict[str, Any]) -> str:
        """Generate main.py file"""
        return f"""
import asyncio
import logging
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    \"\"\"Main application entry point\"\"\"
    config = get_config()
    
    logger.info(f"Starting {{requirements.get('agent_type', 'AI Agent')}} with {{framework}}")
    
    # Initialize your agent here
    # agent = YourAgent(config)
    # await agent.start()
    
    logger.info("Agent started successfully")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    async def process_code_request(self, message: str, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Process code generation request from customer
        
        Args:
            message: Customer message describing requirements
            customer_id: Customer identifier
            language: Customer language
            
        Returns:
            Response dictionary with generated project
        """
        try:
            # Initialize state
            initial_state = AgentState(
                messages=[{"role": "user", "content": message}],
                customer_id=customer_id,
                project_id=None,
                requirements={},
                generated_code={},
                current_step="starting",
                language=language,
                framework="",
                complexity="",
                next_action=""
            )
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state["current_step"] == "completed":
                return {
                    "success": True,
                    "project_id": final_state["project_id"],
                    "framework": final_state["framework"],
                    "complexity": final_state["complexity"],
                    "requirements": final_state["requirements"],
                    "message": "تم إنشاء المشروع بنجاح" if language == "ar" else "Project generated successfully",
                    "next_steps": "يمكنك الآن تنزيل الملفات وبدء التطوير" if language == "ar" else "You can now download files and start development",
                    "estimated_timeline": final_state["requirements"].get("estimated_timeline", "Unknown")
                }
            else:
                return {
                    "success": False,
                    "error": "خطأ في إنشاء المشروع" if language == "ar" else "Error generating project",
                    "current_step": final_state["current_step"]
                }
                
        except Exception as e:
            logger.error(f"Error processing code request: {e}")
            return {
                "success": False,
                "error": "خطأ في معالجة الطلب" if language == "ar" else "Error processing request"
            }