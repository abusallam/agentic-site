"""
OpenRouter Service - LLM provider integration with multiple models
Handles AI model requests with various free and paid models
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OpenRouterService:
    """
    Service for interacting with OpenRouter LLM API
    Provides access to multiple AI models through a unified interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            logger.warning("OpenRouter API key not provided - LLM features will be limited")
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(
            timeout=60.0,  # Longer timeout for LLM requests
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://consulting.sa",
                "X-Title": "Consulting.sa AI Platform"
            } if self.api_key else {"Content-Type": "application/json"}
        )
        
        # Free models available on OpenRouter
        self.free_models = {
            "google/gemma-2-9b-it:free": {
                "name": "Gemma 2 9B",
                "provider": "Google",
                "context_length": 8192,
                "description": "Fast and efficient for general tasks"
            },
            "meta-llama/llama-3.1-8b-instruct:free": {
                "name": "Llama 3.1 8B",
                "provider": "Meta",
                "context_length": 131072,
                "description": "Great for reasoning and code generation"
            },
            "microsoft/phi-3-mini-128k-instruct:free": {
                "name": "Phi-3 Mini",
                "provider": "Microsoft",
                "context_length": 128000,
                "description": "Excellent for long context tasks"
            },
            "qwen/qwen-2-7b-instruct:free": {
                "name": "Qwen 2 7B",
                "provider": "Alibaba",
                "context_length": 32768,
                "description": "Strong multilingual capabilities"
            },
            "google/gemma-2-27b-it:free": {
                "name": "Gemma 2 27B",
                "provider": "Google",
                "context_length": 8192,
                "description": "More powerful version of Gemma"
            }
        }
    
    async def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models
        
        Returns:
            List of available AI models
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "OpenRouter API key not configured",
                    "free_models": self.free_models
                }
            
            response = await self.client.get(f"{self.base_url}/models")
            
            if response.status_code == 200:
                models_data = response.json()
                
                # Filter for free models and add our curated list
                available_models = {}
                for model_id, model_info in self.free_models.items():
                    available_models[model_id] = model_info
                
                logger.info(f"Retrieved {len(available_models)} available models")
                
                return {
                    "success": True,
                    "models": available_models,
                    "total_count": len(available_models),
                    "recommended": "meta-llama/llama-3.1-8b-instruct:free"
                }
            else:
                logger.error(f"Failed to get models: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "free_models": self.free_models
                }
                
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return {
                "success": False,
                "error": str(e),
                "free_models": self.free_models
            }
    
    async def generate_response(self, 
                              prompt: str, 
                              model: str = "meta-llama/llama-3.1-8b-instruct:free",
                              system_prompt: str = None,
                              max_tokens: int = 1000,
                              temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate AI response using specified model
        
        Args:
            prompt: User prompt/question
            model: Model identifier
            system_prompt: Optional system prompt
            max_tokens: Maximum response length
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            AI-generated response
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "OpenRouter API key not configured",
                    "mock_response": f"Mock AI response to: {prompt[:100]}..."
                }
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request payload
            request_payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=request_payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                ai_response = response_data["choices"][0]["message"]["content"]
                usage = response_data.get("usage", {})
                
                logger.info(f"AI response generated using {model} - {usage.get('total_tokens', 0)} tokens")
                
                return {
                    "success": True,
                    "response": ai_response,
                    "model": model,
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    },
                    "generated_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to generate response: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Generation failed: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_customer_message(self, message: str, language: str = "auto") -> Dict[str, Any]:
        """
        Analyze customer message for intent and routing
        
        Args:
            message: Customer message
            language: Message language (auto-detect if not specified)
            
        Returns:
            Message analysis with intent and routing suggestions
        """
        try:
            system_prompt = """You are an AI assistant that analyzes customer messages for a consulting platform. 
            
            Analyze the message and determine:
            1. Primary intent (greeting, question, request, complaint, etc.)
            2. Service category (consulting, technical, billing, workflow)
            3. Urgency level (low, medium, high)
            4. Suggested agent type (initial_customer, n8n_workflow, code_generation, consulting)
            5. Key topics mentioned
            6. Language detected
            
            Respond in JSON format with these fields:
            {
                "intent": "primary intent",
                "category": "service category", 
                "urgency": "urgency level",
                "suggested_agent": "agent type",
                "topics": ["topic1", "topic2"],
                "language": "detected language",
                "confidence": 0.95
            }"""
            
            analysis_result = await self.generate_response(
                prompt=f"Analyze this customer message: {message}",
                system_prompt=system_prompt,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=500,
                temperature=0.3
            )
            
            if analysis_result.get("success"):
                try:
                    # Try to parse JSON response
                    analysis_json = json.loads(analysis_result["response"])
                    
                    return {
                        "success": True,
                        "analysis": analysis_json,
                        "raw_response": analysis_result["response"],
                        "model_used": analysis_result["model"]
                    }
                except json.JSONDecodeError:
                    # Fallback to text analysis
                    return {
                        "success": True,
                        "analysis": {
                            "intent": "general_inquiry",
                            "category": "consulting",
                            "urgency": "medium",
                            "suggested_agent": "initial_customer",
                            "topics": ["general"],
                            "language": language,
                            "confidence": 0.7
                        },
                        "raw_response": analysis_result["response"],
                        "model_used": analysis_result["model"]
                    }
            else:
                return analysis_result
                
        except Exception as e:
            logger.error(f"Error analyzing customer message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_agent_response(self, 
                                    agent_type: str,
                                    customer_message: str,
                                    context: Dict[str, Any] = None,
                                    language: str = "en") -> Dict[str, Any]:
        """
        Generate specialized agent response
        
        Args:
            agent_type: Type of agent (initial_customer, n8n_workflow, etc.)
            customer_message: Customer's message
            context: Additional context information
            language: Response language
            
        Returns:
            Agent-specific response
        """
        try:
            # Agent-specific system prompts
            agent_prompts = {
                "initial_customer": f"""You are a welcoming customer service agent for consulting.sa, an AI consulting platform. 
                Respond in {language}. Be friendly, professional, and helpful. Collect customer information and guide them to appropriate services.
                Keep responses concise and actionable.""",
                
                "n8n_workflow": f"""You are an n8n workflow automation specialist for consulting.sa. 
                Respond in {language}. Help customers create, execute, and manage n8n workflows. 
                Provide technical guidance and template recommendations. Be precise and technical.""",
                
                "code_generation": f"""You are an AI agent development specialist for consulting.sa.
                Respond in {language}. Help customers build AI agents using Google ADK, LangGraph, or Pydantic AI.
                Provide code examples, architecture guidance, and implementation details.""",
                
                "consulting": f"""You are a strategic AI consulting specialist for consulting.sa.
                Respond in {language}. Provide high-level strategic guidance, feasibility analysis, and consultation scheduling.
                Include pricing in Saudi Riyals (SAR) and offer human expert connections."""
            }
            
            system_prompt = agent_prompts.get(agent_type, agent_prompts["initial_customer"])
            
            # Add context if provided
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
                system_prompt += context_str
            
            response_result = await self.generate_response(
                prompt=customer_message,
                system_prompt=system_prompt,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=800,
                temperature=0.7
            )
            
            if response_result.get("success"):
                return {
                    "success": True,
                    "agent_response": response_result["response"],
                    "agent_type": agent_type,
                    "language": language,
                    "model_used": response_result["model"],
                    "usage": response_result.get("usage", {}),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return response_result
                
        except Exception as e:
            logger.error(f"Error generating agent response: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()