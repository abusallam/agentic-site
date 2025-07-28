"""Main entry point for the ADK Agent."""

import logging
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the API server."""
    try:
        logger.info("Starting API server...")
        
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        uvicorn.run(
            "api_server:app",
            host=host,
            port=port,
            reload=os.getenv("ENVIRONMENT") == "development",
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise


if __name__ == "__main__":
    main()
