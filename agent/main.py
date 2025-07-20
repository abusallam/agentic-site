"""Main entry point for the ADK Agent."""

import asyncio
import logging
import os
from dotenv import load_dotenv

from my_adk_agent.agent import AccountantAgent

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the agent."""
    try:
        logger.info("Starting Accountant Agent...")
        
        # Initialize the agent
        agent = AccountantAgent()
        
        # Test the agent with a sample interaction
        test_input = "Hello, I'm interested in creating a chatbot for my business"
        response = await agent.run(test_input)
        
        logger.info("Agent Response:")
        print(response)
        
        logger.info("Accountant Agent is ready!")
        
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())