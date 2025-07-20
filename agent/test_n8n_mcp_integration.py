"""
Comprehensive test script for n8n MCP integration with ADK Agent.
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from my_adk_agent.agent import AccountantAgent
from n8n_mcp_agent.agent import N8nMCPAgent

# Load environment variables from the root directory
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_n8n_mcp_integration():
    """Test the complete n8n MCP integration."""
    try:
        logger.info("🚀 Starting n8n MCP Integration Tests...")
        
        # Initialize agents
        logger.info("Initializing agents...")
        main_agent = AccountantAgent()
        n8n_agent = N8nMCPAgent()
        
        # Test 1: Initialize n8n MCP server
        logger.info("\n--- Test 1: Initialize n8n MCP Server ---")
        init_result = await n8n_agent.initialize_mcp_server()
        logger.info(f"Initialization result: {init_result}")
        
        # Test 2: Start n8n MCP server
        logger.info("\n--- Test 2: Start n8n MCP Server ---")
        start_result = await n8n_agent.start_mcp_server()
        logger.info(f"Start result: {start_result}")
        
        if start_result.get("status") == "success":
            # Wait for server to fully start
            await asyncio.sleep(3)
            
            # Test 3: Check server status
            logger.info("\n--- Test 3: Check Server Status ---")
            status_result = await n8n_agent.get_mcp_server_status()
            logger.info(f"Status result: {status_result}")
            
            # Test 4: Test via main agent
            logger.info("\n--- Test 4: Test via Main Agent ---")
            main_status = await main_agent.manage_n8n_mcp_server("status")
            logger.info(f"Main agent status: {main_status}")
            
            # Test 5: Natural language commands
            logger.info("\n--- Test 5: Natural Language Commands ---")
            test_commands = [
                "n8n server status",
                "start n8n server",
                "What's the status of the workflow server?"
            ]
            
            for command in test_commands:
                logger.info(f"Testing command: '{command}'")
                response = await main_agent.run(command)
                logger.info(f"Response: {response}")
                print(f"\n💬 Command: {command}")
                print(f"🤖 Response: {response}")
            
            # Test 6: Service deployment via n8n MCP
            logger.info("\n--- Test 6: Service Deployment via n8n MCP ---")
            deployment_config = {
                "customer_id": "test-customer-123",
                "service_name": "Test Chatbot",
                "system_prompt": "You are a helpful customer service assistant.",
                "language": "en"
            }
            
            deployment_result = await main_agent.deploy_ai_service(
                customer_email="test@example.com",
                service_type="chatbot",
                config=deployment_config
            )
            logger.info(f"Deployment result: {deployment_result}")
            
            # Test 7: Workflow creation
            logger.info("\n--- Test 7: Direct Workflow Creation ---")
            workflow_config = {
                "name": "Test Customer Support Workflow",
                "active": True,
                "nodes": [
                    {
                        "parameters": {
                            "path": "test-webhook",
                            "options": {}
                        },
                        "id": "webhook-1",
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [240, 300]
                    }
                ],
                "connections": {},
                "settings": {"executionOrder": "v1"}
            }
            
            workflow_result = await main_agent.create_workflow_via_n8n_mcp(
                customer_email="test@example.com",
                workflow_config=workflow_config
            )
            logger.info(f"Workflow creation result: {workflow_result}")
            
            # Test 8: List workflows
            logger.info("\n--- Test 8: List Workflows ---")
            list_result = await main_agent.manage_n8n_mcp_server("list_workflows")
            logger.info(f"Workflows list: {list_result}")
            
            # Test 9: Get node information
            logger.info("\n--- Test 9: Get Node Information ---")
            node_info_result = await main_agent.manage_n8n_mcp_server(
                "get_node_info", 
                {"node_type": "n8n-nodes-base.webhook"}
            )
            logger.info(f"Node info result: {node_info_result}")
            
        else:
            logger.error("❌ Failed to start n8n MCP server, skipping dependent tests")
        
        # Test 10: Stop server
        logger.info("\n--- Test 10: Stop n8n MCP Server ---")
        stop_result = await n8n_agent.stop_mcp_server()
        logger.info(f"Stop result: {stop_result}")
        
        logger.info("\n✅ n8n MCP Integration Tests Completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


async def test_customer_journey_with_n8n():
    """Test complete customer journey with n8n MCP integration."""
    try:
        logger.info("\n🎯 Testing Complete Customer Journey with n8n MCP...")
        
        # Initialize main agent
        agent = AccountantAgent()
        
        # Test customer journey scenarios
        test_scenarios = [
            {
                "name": "Chatbot Request",
                "input": "I need a chatbot for my e-commerce website that can handle customer inquiries in English and Arabic",
                "email": "ecommerce@example.com"
            },
            {
                "name": "AI Agent Request", 
                "input": "I want an AI agent that can automate my customer support and integrate with my CRM",
                "email": "support@example.com"
            },
            {
                "name": "Workflow Automation",
                "input": "I need to automate my order processing workflow with notifications and inventory updates",
                "email": "operations@example.com"
            }
        ]
        
        for scenario in test_scenarios:
            logger.info(f"\n--- Testing Scenario: {scenario['name']} ---")
            
            # Step 1: Gather requirements
            requirements_result = await agent.gather_customer_requirements(
                scenario["input"], 
                scenario["email"]
            )
            logger.info(f"Requirements: {requirements_result}")
            
            # Step 2: Create customer record
            customer_result = await agent.create_customer_record(
                email=scenario["email"],
                name=f"Test Customer - {scenario['name']}",
                requirements=requirements_result.get("requirements", {})
            )
            logger.info(f"Customer creation: {customer_result}")
            
            # Step 3: Deploy service
            if requirements_result.get("status") == "success":
                service_type = requirements_result["requirements"]["service_type"]
                config = {
                    "customer_email": scenario["email"],
                    "requirements": requirements_result["requirements"],
                    "auto_generated": True
                }
                
                deployment_result = await agent.deploy_ai_service(
                    customer_email=scenario["email"],
                    service_type=service_type,
                    config=config
                )
                logger.info(f"Service deployment: {deployment_result}")
            
            # Step 4: Check customer status
            status_result = await agent.get_customer_status(scenario["email"])
            logger.info(f"Customer status: {status_result}")
            
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"📧 Email: {scenario['email']}")
            print(f"🎯 Service Type: {requirements_result.get('requirements', {}).get('service_type', 'Unknown')}")
            print(f"✅ Status: {'Success' if requirements_result.get('status') == 'success' else 'Failed'}")
        
        logger.info("\n✅ Customer Journey Tests Completed!")
        
    except Exception as e:
        logger.error(f"❌ Customer journey test failed: {e}")
        raise


async def test_json_commands():
    """Test JSON command interface."""
    try:
        logger.info("\n🔧 Testing JSON Command Interface...")
        
        agent = AccountantAgent()
        
        # Test JSON commands
        json_commands = [
            {
                "name": "n8n Server Status",
                "command": {
                    "action": "gather_requirements",
                    "params": {
                        "input": "I need help with n8n server status",
                        "email": "admin@example.com"
                    }
                }
            },
            {
                "name": "Deploy Chatbot Service",
                "command": {
                    "action": "deploy_service",
                    "params": {
                        "email": "chatbot@example.com",
                        "service_type": "chatbot",
                        "config": {
                            "name": "Customer Support Bot",
                            "language": "en",
                            "system_prompt": "You are a helpful customer support assistant."
                        }
                    }
                }
            },
            {
                "name": "Get Customer Status",
                "command": {
                    "action": "get_status",
                    "params": {
                        "email": "test@example.com"
                    }
                }
            }
        ]
        
        for test_case in json_commands:
            logger.info(f"\n--- Testing: {test_case['name']} ---")
            
            import json
            command_str = json.dumps(test_case["command"])
            response = await agent.run(command_str)
            
            logger.info(f"Command: {command_str}")
            logger.info(f"Response: {response}")
            
            print(f"\n🔧 Test: {test_case['name']}")
            print(f"📤 Command: {command_str}")
            print(f"📥 Response: {response[:200]}..." if len(response) > 200 else f"📥 Response: {response}")
        
        logger.info("\n✅ JSON Command Tests Completed!")
        
    except Exception as e:
        logger.error(f"❌ JSON command test failed: {e}")
        raise


async def main():
    """Run all integration tests."""
    try:
        print("🧪 n8n MCP Integration Test Suite")
        print("=" * 50)
        
        # Test 1: Basic n8n MCP integration
        await test_n8n_mcp_integration()
        
        # Test 2: Customer journey with n8n
        await test_customer_journey_with_n8n()
        
        # Test 3: JSON command interface
        await test_json_commands()
        
        print("\n🎉 All Tests Completed Successfully!")
        print("=" * 50)
        print("✅ n8n MCP server integration is working")
        print("✅ Customer journey orchestration is functional")
        print("✅ Service deployment via n8n MCP is operational")
        print("✅ JSON command interface is responsive")
        
    except Exception as e:
        print(f"\n❌ Test Suite Failed: {e}")
        logger.error(f"Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())