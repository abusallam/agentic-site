"""
Intelligent Agent Router - Routes messages to appropriate agents
Handles context preservation and agent handoffs
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .agents.initial_customer_agent import InitialCustomerAgent
from .agents.n8n_workflow_agent import N8nWorkflowAgent
from .agents.code_generation_agent import CodeGenerationAgent
from .agents.consulting_agent import ConsultingAgent
from .agents.billing_agent import BillingAgent
from .services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Intelligent router that selects the most appropriate agent for each message
    - Analyzes message content and context
    - Routes to specialized agents based on customer needs
    - Maintains conversation context across agent handoffs
    - Provides fallback mechanisms for agent failures
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supabase = SupabaseService(config)
        
        # Initialize all agents
        self.agents = {
            'initial_customer': InitialCustomerAgent(config),
            'n8n_workflow': N8nWorkflowAgent(config),
            'code_generation': CodeGenerationAgent(config),
            'consulting': ConsultingAgent(config),
            'billing': BillingAgent(config)
        }
        
        # Agent routing keywords
        self.routing_keywords = {
            'initial_customer': {
                'ar': ['مرحبا', 'السلام عليكم', 'أهلا', 'معلومات', 'خدمات', 'شركة', 'تعريف'],
                'en': ['hello', 'hi', 'welcome', 'information', 'services', 'company', 'about']
            },
            'n8n_workflow': {
                'ar': ['أتمتة', 'سير العمل', 'workflow', 'n8n', 'تنفيذ', 'عملية', 'تلقائي'],
                'en': ['automation', 'workflow', 'n8n', 'execute', 'process', 'automatic', 'template']
            },
            'code_generation': {
                'ar': ['كود', 'برمجة', 'تطوير', 'نظام', 'تطبيق', 'مشروع', 'تقني'],
                'en': ['code', 'programming', 'development', 'system', 'application', 'project', 'technical']
            },
            'consulting': {
                'ar': ['استشارة', 'مشورة', 'خبير', 'مستشار', 'تحليل', 'استراتيجية', 'خطة'],
                'en': ['consulting', 'consultation', 'expert', 'consultant', 'analysis', 'strategy', 'plan']
            },
            'billing': {
                'ar': ['فاتورة', 'دفع', 'تكلفة', 'سعر', 'استخدام', 'حساب', 'مالي'],
                'en': ['billing', 'payment', 'cost', 'price', 'usage', 'invoice', 'financial']
            }
        }
        
        # Agent capabilities for intelligent routing
        self.agent_capabilities = {
            'initial_customer': {
                'handles': ['greeting', 'information_request', 'service_inquiry', 'contact_info'],
                'complexity': 'low',
                'languages': ['ar', 'en'],
                'handoff_to': ['n8n_workflow', 'code_generation', 'consulting', 'billing']
            },
            'n8n_workflow': {
                'handles': ['workflow_automation', 'template_creation', 'execution_monitoring'],
                'complexity': 'medium',
                'languages': ['ar', 'en'],
                'requires_auth': True,
                'handoff_to': ['consulting', 'billing']
            },
            'code_generation': {
                'handles': ['custom_development', 'architecture_design', 'framework_selection'],
                'complexity': 'high',
                'languages': ['en'],
                'handoff_to': ['consulting', 'billing']
            },
            'consulting': {
                'handles': ['strategic_advice', 'business_analysis', 'human_consultation'],
                'complexity': 'high',
                'languages': ['ar', 'en'],
                'handoff_to': ['billing']
            },
            'billing': {
                'handles': ['resource_tracking', 'invoice_generation', 'payment_processing'],
                'complexity': 'medium',
                'languages': ['ar', 'en'],
                'handoff_to': []
            }
        }
    
    async def route_message(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route message to the most appropriate agent
        
        Args:
            message: Customer message
            session_id: Session identifier
            context: Additional context information
            
        Returns:
            Agent response with routing information
        """
        try:
            # Get or create conversation context
            conversation_context = await self._get_conversation_context(session_id)
            
            # Update context with new message
            conversation_context['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Detect language
            language = self._detect_language(message)
            conversation_context['language'] = language
            
            # Determine best agent for this message
            selected_agent_type = await self._select_agent(message, conversation_context, context)
            
            # Get the selected agent
            selected_agent = self.agents[selected_agent_type]
            
            # Process message with selected agent
            if selected_agent_type == 'initial_customer':
                response = await selected_agent.process_message(message, session_id)
            elif selected_agent_type == 'n8n_workflow':
                customer_id = conversation_context.get('customer_id')
                response = await selected_agent.process_workflow_request(message, customer_id, language)
            elif selected_agent_type == 'code_generation':
                customer_id = conversation_context.get('customer_id')
                response = await selected_agent.process_code_request(message, customer_id, language)
            elif selected_agent_type == 'consulting':
                customer_id = conversation_context.get('customer_id')
                response = await selected_agent.process_consultation_message(message, customer_id, language)
            elif selected_agent_type == 'billing':
                customer_id = conversation_context.get('customer_id')
                response = await selected_agent.process_billing_message(message, customer_id, language)
            else:
                # Fallback to initial customer agent
                response = await self.agents['initial_customer'].process_message(message, session_id)
            
            # Update conversation context
            conversation_context['current_agent'] = selected_agent_type
            conversation_context['messages'].append({
                'role': 'assistant',
                'content': response.get('content', ''),
                'agent': selected_agent_type,
                'timestamp': datetime.now().isoformat()
            })
            
            # Save updated context
            await self._save_conversation_context(session_id, conversation_context)
            
            # Add routing information to response
            response['routing'] = {
                'selected_agent': selected_agent_type,
                'confidence': self._calculate_routing_confidence(message, selected_agent_type),
                'alternative_agents': self._get_alternative_agents(message, selected_agent_type),
                'handoff_available': len(self.agent_capabilities[selected_agent_type]['handoff_to']) > 0
            }
            
            logger.info(f"Routed message to {selected_agent_type} agent for session {session_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            
            # Fallback to initial customer agent
            try:
                fallback_response = await self.agents['initial_customer'].process_message(message, session_id)
                fallback_response['routing'] = {
                    'selected_agent': 'initial_customer',
                    'confidence': 0.5,
                    'fallback': True,
                    'error': str(e)
                }
                return fallback_response
            except Exception as fallback_error:
                logger.error(f"Fallback routing failed: {fallback_error}")
                return {
                    'content': 'عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.' if language == 'ar' else 'Sorry, a system error occurred. Please try again.',
                    'language': language,
                    'agent_type': 'error',
                    'routing': {
                        'selected_agent': 'error',
                        'confidence': 0.0,
                        'error': str(e)
                    }
                }
    
    async def _select_agent(self, message: str, conversation_context: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Select the most appropriate agent for the message"""
        
        # Check current agent and conversation flow
        current_agent = conversation_context.get('current_agent')
        customer_id = conversation_context.get('customer_id')
        language = conversation_context.get('language', 'ar')
        
        # Calculate scores for each agent
        agent_scores = {}
        
        for agent_type, agent in self.agents.items():
            score = 0.0
            
            # Keyword matching
            keywords = self.routing_keywords.get(agent_type, {}).get(language, [])
            message_lower = message.lower()
            
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1.0
            
            # Language compatibility
            if language in self.agent_capabilities[agent_type]['languages']:
                score += 0.5
            
            # Authentication requirements
            if self.agent_capabilities[agent_type].get('requires_auth', False):
                if customer_id:
                    score += 0.5
                else:
                    score -= 1.0  # Penalize if auth required but not available
            
            # Conversation continuity
            if current_agent == agent_type:
                score += 0.3  # Slight preference for current agent
            
            # Handoff capability
            if current_agent and agent_type in self.agent_capabilities.get(current_agent, {}).get('handoff_to', []):
                score += 0.4
            
            agent_scores[agent_type] = score
        
        # Special routing logic
        message_lower = message.lower()
        
        # Force routing for specific patterns
        if any(word in message_lower for word in ['فاتورة', 'دفع', 'تكلفة', 'billing', 'payment', 'cost', 'invoice']):
            return 'billing'
        
        if any(word in message_lower for word in ['أتمتة', 'workflow', 'n8n', 'automation', 'template']):
            if customer_id:  # Only if authenticated
                return 'n8n_workflow'
        
        if any(word in message_lower for word in ['كود', 'برمجة', 'code', 'programming', 'development']):
            return 'code_generation'
        
        if any(word in message_lower for word in ['استشارة', 'مستشار', 'consulting', 'consultant', 'expert']):
            return 'consulting'
        
        # Default routing based on scores
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        
        # If no clear winner, use initial customer agent
        if best_agent[1] < 0.5:
            return 'initial_customer'
        
        return best_agent[0]
    
    def _detect_language(self, message: str) -> str:
        """Detect message language"""
        # Simple Arabic detection based on character range
        arabic_chars = sum(1 for char in message if '\u0600' <= char <= '\u06FF')
        total_chars = len([char for char in message if char.isalpha()])
        
        if total_chars == 0:
            return 'ar'  # Default to Arabic
        
        arabic_ratio = arabic_chars / total_chars
        return 'ar' if arabic_ratio > 0.3 else 'en'
    
    def _calculate_routing_confidence(self, message: str, selected_agent: str) -> float:
        """Calculate confidence score for routing decision"""
        # Simple confidence calculation based on keyword matches
        language = self._detect_language(message)
        keywords = self.routing_keywords.get(selected_agent, {}).get(language, [])
        
        matches = sum(1 for keyword in keywords if keyword in message.lower())
        max_possible_matches = len(keywords)
        
        if max_possible_matches == 0:
            return 0.5  # Default confidence
        
        base_confidence = matches / max_possible_matches
        
        # Boost confidence for exact matches
        if matches > 0:
            base_confidence = min(1.0, base_confidence + 0.2)
        
        return base_confidence
    
    def _get_alternative_agents(self, message: str, selected_agent: str) -> List[str]:
        """Get alternative agents that could handle this message"""
        language = self._detect_language(message)
        alternatives = []
        
        for agent_type, agent_info in self.agent_capabilities.items():
            if agent_type != selected_agent and language in agent_info['languages']:
                # Check if agent could potentially handle this message
                keywords = self.routing_keywords.get(agent_type, {}).get(language, [])
                if any(keyword in message.lower() for keyword in keywords):
                    alternatives.append(agent_type)
        
        return alternatives[:2]  # Return top 2 alternatives
    
    async def _get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context from database"""
        try:
            context = await self.supabase.get_conversation_context(session_id)
            if context:
                return context
        except Exception as e:
            logger.warning(f"Could not retrieve conversation context: {e}")
        
        # Return default context
        return {
            'session_id': session_id,
            'messages': [],
            'current_agent': None,
            'customer_id': None,
            'language': 'ar',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    async def _save_conversation_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Save conversation context to database"""
        try:
            context['updated_at'] = datetime.now().isoformat()
            await self.supabase.save_conversation_context(session_id, context)
        except Exception as e:
            logger.error(f"Could not save conversation context: {e}")
    
    async def handoff_to_agent(self, session_id: str, target_agent: str, reason: str = None) -> Dict[str, Any]:
        """
        Manually handoff conversation to specific agent
        
        Args:
            session_id: Session identifier
            target_agent: Target agent type
            reason: Reason for handoff
            
        Returns:
            Handoff result
        """
        try:
            if target_agent not in self.agents:
                return {
                    'success': False,
                    'error': f'Unknown agent type: {target_agent}'
                }
            
            # Get conversation context
            context = await self._get_conversation_context(session_id)
            
            # Update context with handoff information
            context['current_agent'] = target_agent
            context['handoff_history'] = context.get('handoff_history', [])
            context['handoff_history'].append({
                'to_agent': target_agent,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
            
            # Save updated context
            await self._save_conversation_context(session_id, context)
            
            logger.info(f"Handed off session {session_id} to {target_agent} agent")
            
            return {
                'success': True,
                'target_agent': target_agent,
                'message': f'تم تحويلك إلى {target_agent}' if context.get('language') == 'ar' else f'Transferred to {target_agent} agent'
            }
            
        except Exception as e:
            logger.error(f"Error in agent handoff: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            'total_agents': len(self.agents),
            'agents': {},
            'routing_active': True,
            'timestamp': datetime.now().isoformat()
        }
        
        for agent_type, agent in self.agents.items():
            try:
                # Basic health check for each agent
                status['agents'][agent_type] = {
                    'status': 'healthy',
                    'capabilities': self.agent_capabilities.get(agent_type, {}),
                    'keywords': self.routing_keywords.get(agent_type, {})
                }
            except Exception as e:
                status['agents'][agent_type] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return status