"""Test script for the ADK Agent."""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from my_adk_agent.agent import AccountantAgent

# Load environment variables from the root directory
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_agent():
    """Test the agent with various scenarios."""
    try:
        logger.info("Initializing Accountant Agent...")
        agent = AccountantAgent()
        
        # Test scenarios
        test_cases = [
            "Hello, I'm interested in creating a chatbot for my business",
            "I need an AI agent that can handle customer support",
            "What are your pricing options?",
            "I want to automate my workflow processes",
            '{"action": "gather_requirements", "params": {"input": "I need a multilingual chatbot", "email": "test@example.com"}}'
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            logger.info(f"\n--- Test Case {i} ---")
            logger.info(f"Input: {test_input}")
            
            try:
                response = await agent.run(test_input)
                logger.info(f"Response: {response}")
            except Exception as e:
                logger.error(f"Error in test case {i}: {e}")
        
        logger.info("\n--- Testing Individual Tools ---")
        
        # Test individual tools
        try:
            # Test requirements gathering
            result = await agent.gather_customer_requirements(
                "I need a chatbot for my e-commerce website",
                "test@example.com"
            )
            logger.info(f"Requirements gathering result: {result}")
            
            # Test customer creation
            result = await agent.create_customer_record(
                email="test@example.com",
                name="Test Customer",
                requirements={"service_type": "chatbot"}
            )
            logger.info(f"Customer creation result: {result}")
            
            # Test status check
            result = await agent.get_customer_status("test@example.com")
            logger.info(f"Customer status result: {result}")
            
        except Exception as e:
            logger.error(f"Error testing individual tools: {e}")
        
        logger.info("\nAgent testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to test agent: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_agent())