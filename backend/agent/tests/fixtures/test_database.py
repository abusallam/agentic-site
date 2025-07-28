#!/usr/bin/env python3
"""
Test Database Setup and Teardown Automation

This module provides automated test database setup, teardown, and management
for integration testing of the agentic AI platform.
"""

import asyncio
import os
import json
import tempfile
import shutil
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TestDatabaseManager:
    """
    Manages test database lifecycle for integration testing
    """
    
    def __init__(self, test_mode: str = "sqlite"):
        self.test_mode = test_mode  # sqlite, postgres, or mock
        self.test_db_path = None
        self.temp_dir = None
        self.db_connection = None
        self.test_data = {}
        
    async def setup_test_database(self) -> Dict[str, Any]:
        """
        Set up test database with required schema and test data
        """
        logger.info(f"Setting up test database in {self.test_mode} mode...")
        
        try:
            if self.test_mode == "sqlite":
                return await self._setup_sqlite_test_db()
            elif self.test_mode == "postgres":
                return await self._setup_postgres_test_db()
            elif self.test_mode == "mock":
                return await self._setup_mock_database()
            else:
                raise ValueError(f"Unsupported test mode: {self.test_mode}")
                
        except Exception as e:
            logger.error(f"Failed to setup test database: {e}")
            raise
    
    async def _setup_sqlite_test_db(self) -> Dict[str, Any]:
        """
        Set up SQLite test database
        """
        import sqlite3
        
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp(prefix="agentic_test_")
        self.test_db_path = os.path.join(self.temp_dir, "test_database.db")
        
        # Create database connection
        self.db_connection = sqlite3.connect(self.test_db_path)
        self.db_connection.row_factory = sqlite3.Row
        
        # Create test schema
        await self._create_test_schema()
        
        # Insert test data
        await self._insert_test_data()
        
        return {
            "status": "ready",
            "database_type": "sqlite",
            "database_path": self.test_db_path,
            "temp_directory": self.temp_dir,
            "tables_created": ["customers", "conversations", "metrics", "workflows"]
        }
    
    async def _setup_postgres_test_db(self) -> Dict[str, Any]:
        """
        Set up PostgreSQL test database (requires asyncpg)
        """
        try:
            import asyncpg
        except ImportError:
            logger.warning("asyncpg not available, falling back to mock mode")
            return await self._setup_mock_database()
        
        # Use test database URL or create temporary one
        test_db_url = os.getenv("TEST_DATABASE_URL")
        if not test_db_url:
            logger.warning("TEST_DATABASE_URL not set, falling back to mock mode")
            return await self._setup_mock_database()
        
        try:
            # Connect to test database
            self.db_connection = await asyncpg.connect(test_db_url)
            
            # Create test schema
            await self._create_postgres_schema()
            
            # Insert test data
            await self._insert_postgres_test_data()
            
            return {
                "status": "ready",
                "database_type": "postgres",
                "database_url": test_db_url,
                "tables_created": ["customers", "conversations", "metrics", "workflows"]
            }
            
        except Exception as e:
            logger.error(f"Failed to setup PostgreSQL test database: {e}")
            logger.info("Falling back to mock database")
            return await self._setup_mock_database()
    
    async def _setup_mock_database(self) -> Dict[str, Any]:
        """
        Set up mock in-memory database
        """
        self.test_data = {
            "customers": {},
            "conversations": {},
            "metrics": {},
            "workflows": {}
        }
        
        # Pre-populate with test data
        await self._populate_mock_data()
        
        return {
            "status": "ready",
            "database_type": "mock",
            "tables_created": list(self.test_data.keys()),
            "records_count": {table: len(data) for table, data in self.test_data.items()}
        }
    
    async def _create_test_schema(self):
        """
        Create test database schema for SQLite
        """
        cursor = self.db_connection.cursor()
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                requirements TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                messages TEXT NOT NULL,  -- JSON string
                status TEXT DEFAULT 'active',
                topic TEXT,
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                metric_data TEXT NOT NULL,  -- JSON string
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                execution_id TEXT,
                status TEXT DEFAULT 'pending',
                payload TEXT,  -- JSON string
                result TEXT,   -- JSON string
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        self.db_connection.commit()
        logger.info("Test database schema created successfully")
    
    async def _create_postgres_schema(self):
        """
        Create test database schema for PostgreSQL
        """
        # Customers table
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                requirements TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Conversations table
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                messages JSONB NOT NULL,
                status TEXT DEFAULT 'active',
                topic TEXT,
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Metrics table
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                metric_data JSONB NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Workflows table
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                execution_id TEXT,
                status TEXT DEFAULT 'pending',
                payload JSONB,
                result JSONB,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        """)
        
        logger.info("PostgreSQL test database schema created successfully")
    
    async def _insert_test_data(self):
        """
        Insert test data into SQLite database
        """
        cursor = self.db_connection.cursor()
        
        # Test customers
        test_customers = [
            ("cust_001", "john.doe@example.com", "John Doe", "Tech Corp", "+1-555-0001", "AI automation", "active"),
            ("cust_002", "jane.smith@example.com", "Jane Smith", "Innovation Inc", "+1-555-0002", "Chatbot development", "active"),
            ("cust_003", "bob.wilson@example.com", "Bob Wilson", "Future Systems", "+1-555-0003", "Process automation", "pending")
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO customers (id, email, name, company, phone, requirements, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, test_customers)
        
        # Test conversations
        test_conversations = [
            ("conv_001", "cust_001", json.dumps([
                {"role": "user", "content": "I need help with AI implementation"},
                {"role": "assistant", "content": "I'd be happy to help you with AI implementation."}
            ]), "active", "AI Implementation", "high"),
            ("conv_002", "cust_002", json.dumps([
                {"role": "user", "content": "Can you help me build a chatbot?"},
                {"role": "assistant", "content": "Absolutely! Let's discuss your chatbot requirements."}
            ]), "active", "Chatbot Development", "medium")
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO conversations (id, customer_id, messages, status, topic, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_conversations)
        
        # Test metrics
        test_metrics = [
            ("metric_001", "system_performance", json.dumps({
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time": 1.23
            })),
            ("metric_002", "user_activity", json.dumps({
                "active_users": 150,
                "new_conversations": 25,
                "completed_workflows": 12
            }))
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO metrics (id, metric_type, metric_data)
            VALUES (?, ?, ?)
        """, test_metrics)
        
        # Test workflows
        test_workflows = [
            ("workflow_001", "customer_onboarding", "exec_001", "completed", 
             json.dumps({"customer_id": "cust_001"}), 
             json.dumps({"status": "success", "steps_completed": 5})),
            ("workflow_002", "notification_workflow", "exec_002", "running",
             json.dumps({"type": "email", "recipient": "jane.smith@example.com"}),
             None)
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO workflows (id, name, execution_id, status, payload, result)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_workflows)
        
        self.db_connection.commit()
        logger.info("Test data inserted successfully")
    
    async def _insert_postgres_test_data(self):
        """
        Insert test data into PostgreSQL database
        """
        # Similar to SQLite but using asyncpg syntax
        # Test customers
        await self.db_connection.executemany("""
            INSERT INTO customers (id, email, name, company, phone, requirements, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                name = EXCLUDED.name,
                updated_at = NOW()
        """, [
            ("cust_001", "john.doe@example.com", "John Doe", "Tech Corp", "+1-555-0001", "AI automation", "active"),
            ("cust_002", "jane.smith@example.com", "Jane Smith", "Innovation Inc", "+1-555-0002", "Chatbot development", "active"),
            ("cust_003", "bob.wilson@example.com", "Bob Wilson", "Future Systems", "+1-555-0003", "Process automation", "pending")
        ])
        
        logger.info("PostgreSQL test data inserted successfully")
    
    async def _populate_mock_data(self):
        """
        Populate mock database with test data
        """
        # Mock customers
        self.test_data["customers"] = {
            "cust_001": {
                "id": "cust_001",
                "email": "john.doe@example.com",
                "name": "John Doe",
                "company": "Tech Corp",
                "phone": "+1-555-0001",
                "requirements": "AI automation",
                "status": "active",
                "created_at": "2025-01-23T10:00:00Z"
            },
            "cust_002": {
                "id": "cust_002",
                "email": "jane.smith@example.com",
                "name": "Jane Smith",
                "company": "Innovation Inc",
                "phone": "+1-555-0002",
                "requirements": "Chatbot development",
                "status": "active",
                "created_at": "2025-01-23T10:15:00Z"
            }
        }
        
        # Mock conversations
        self.test_data["conversations"] = {
            "conv_001": {
                "id": "conv_001",
                "customer_id": "cust_001",
                "messages": [
                    {"role": "user", "content": "I need help with AI implementation"},
                    {"role": "assistant", "content": "I'd be happy to help you with AI implementation."}
                ],
                "status": "active",
                "topic": "AI Implementation",
                "priority": "high",
                "created_at": "2025-01-23T10:30:00Z"
            }
        }
        
        # Mock metrics
        self.test_data["metrics"] = {
            "metric_001": {
                "id": "metric_001",
                "metric_type": "system_performance",
                "metric_data": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "response_time": 1.23
                },
                "timestamp": "2025-01-23T10:45:00Z"
            }
        }
        
        # Mock workflows
        self.test_data["workflows"] = {
            "workflow_001": {
                "id": "workflow_001",
                "name": "customer_onboarding",
                "execution_id": "exec_001",
                "status": "completed",
                "payload": {"customer_id": "cust_001"},
                "result": {"status": "success", "steps_completed": 5},
                "started_at": "2025-01-23T11:00:00Z",
                "completed_at": "2025-01-23T11:05:00Z"
            }
        }
        
        logger.info("Mock test data populated successfully")
    
    async def get_test_data(self, table: str, record_id: Optional[str] = None) -> Any:
        """
        Retrieve test data from database
        """
        if self.test_mode == "mock":
            if record_id:
                return self.test_data.get(table, {}).get(record_id)
            return self.test_data.get(table, {})
        
        elif self.test_mode == "sqlite":
            cursor = self.db_connection.cursor()
            if record_id:
                cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        elif self.test_mode == "postgres":
            if record_id:
                row = await self.db_connection.fetchrow(f"SELECT * FROM {table} WHERE id = $1", record_id)
                return dict(row) if row else None
            else:
                rows = await self.db_connection.fetch(f"SELECT * FROM {table}")
                return [dict(row) for row in rows]
    
    async def cleanup_test_database(self) -> Dict[str, Any]:
        """
        Clean up test database and temporary files
        """
        logger.info("Cleaning up test database...")
        
        try:
            if self.test_mode == "sqlite":
                if self.db_connection:
                    self.db_connection.close()
                if self.temp_dir and os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                    
            elif self.test_mode == "postgres":
                if self.db_connection:
                    await self.db_connection.close()
                    
            elif self.test_mode == "mock":
                self.test_data.clear()
            
            return {
                "status": "cleaned",
                "database_type": self.test_mode,
                "cleanup_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {
                "status": "error",
                "error": str(e),
                "cleanup_completed": False
            }
    
    async def reset_test_database(self) -> Dict[str, Any]:
        """
        Reset test database to initial state
        """
        logger.info("Resetting test database...")
        
        await self.cleanup_test_database()
        return await self.setup_test_database()
    
    async def verify_test_database(self) -> Dict[str, Any]:
        """
        Verify test database integrity and data
        """
        logger.info("Verifying test database...")
        
        try:
            verification_results = {
                "database_type": self.test_mode,
                "tables_verified": [],
                "data_integrity": True,
                "issues": []
            }
            
            # Verify each table
            for table in ["customers", "conversations", "metrics", "workflows"]:
                data = await self.get_test_data(table)
                if data:
                    verification_results["tables_verified"].append(table)
                    logger.info(f"Table {table}: {len(data) if isinstance(data, list) else len(data)} records")
                else:
                    verification_results["issues"].append(f"Table {table} is empty or missing")
            
            if len(verification_results["issues"]) > 0:
                verification_results["data_integrity"] = False
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return {
                "database_type": self.test_mode,
                "data_integrity": False,
                "error": str(e),
                "issues": [f"Verification failed: {str(e)}"]
            }

# Pytest fixtures for database testing
import pytest

@pytest.fixture(scope="session")
async def test_db_manager():
    """Session-scoped test database manager"""
    manager = TestDatabaseManager(test_mode=os.getenv('TEST_DB_MODE', 'mock'))
    setup_result = await manager.setup_test_database()
    
    yield manager, setup_result
    
    # Cleanup after all tests
    await manager.cleanup_test_database()

@pytest.fixture
async def clean_test_db(test_db_manager):
    """Function-scoped clean database for each test"""
    manager, setup_result = test_db_manager
    
    # Reset database to clean state before each test
    await manager.reset_test_database()
    
    yield manager
    
    # Optional: cleanup after each test (already handled by reset)

@pytest.fixture
def sample_customer_data():
    """Fixture providing sample customer data for testing"""
    return {
        "email": "test.customer@example.com",
        "name": "Test Customer",
        "company": "Test Company Inc",
        "phone": "+1-555-0123",
        "requirements": "AI consulting services for customer support automation"
    }

@pytest.fixture
def sample_conversation_data():
    """Fixture providing sample conversation data for testing"""
    return {
        "messages": [
            {"role": "user", "content": "Hello, I need help with AI implementation"},
            {"role": "assistant", "content": "I'd be happy to help you with AI implementation. What specific area are you looking to implement AI in?"},
            {"role": "user", "content": "Customer service automation with chatbots"}
        ],
        "status": "active",
        "topic": "AI Implementation",
        "priority": "high"
    }

@pytest.fixture
def sample_metrics_data():
    """Fixture providing sample metrics data for testing"""
    return {
        "metric_type": "system_performance",
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 34.1,
        "response_time": 1.23,
        "request_count": 150,
        "error_count": 2
    }

@pytest.fixture
def sample_workflow_data():
    """Fixture providing sample workflow data for testing"""
    return {
        "name": "customer_onboarding",
        "payload": {
            "customer_id": "test_customer_123",
            "email": "test@example.com",
            "onboarding_type": "premium"
        },
        "status": "pending"
    }

# Test database operations
@pytest.mark.asyncio
async def test_database_setup(test_db_manager):
    """Test database setup and initialization"""
    manager, setup_result = test_db_manager
    
    assert setup_result["status"] == "ready"
    assert "tables_created" in setup_result
    assert len(setup_result["tables_created"]) > 0

@pytest.mark.asyncio
async def test_database_verification(test_db_manager):
    """Test database verification functionality"""
    manager, _ = test_db_manager
    
    verification_result = await manager.verify_test_database()
    
    assert "database_type" in verification_result
    assert "data_integrity" in verification_result
    assert "tables_verified" in verification_result

@pytest.mark.asyncio
async def test_customer_operations(clean_test_db, sample_customer_data):
    """Test customer CRUD operations"""
    manager = clean_test_db
    
    # Test data insertion (mock mode)
    if manager.test_mode == "mock":
        customer_id = f"test_customer_{int(time.time())}"
        manager.test_data["customers"][customer_id] = {
            "id": customer_id,
            **sample_customer_data,
            "created_at": time.time()
        }
        
        # Test data retrieval
        retrieved_customer = await manager.get_test_data("customers", customer_id)
        assert retrieved_customer is not None
        assert retrieved_customer["email"] == sample_customer_data["email"]
        assert retrieved_customer["name"] == sample_customer_data["name"]

@pytest.mark.asyncio
async def test_conversation_operations(clean_test_db, sample_conversation_data):
    """Test conversation CRUD operations"""
    manager = clean_test_db
    
    if manager.test_mode == "mock":
        conversation_id = f"test_conversation_{int(time.time())}"
        manager.test_data["conversations"][conversation_id] = {
            "id": conversation_id,
            "customer_id": "test_customer_123",
            **sample_conversation_data,
            "created_at": time.time()
        }
        
        # Test data retrieval
        retrieved_conversation = await manager.get_test_data("conversations", conversation_id)
        assert retrieved_conversation is not None
        assert retrieved_conversation["topic"] == sample_conversation_data["topic"]
        assert len(retrieved_conversation["messages"]) == len(sample_conversation_data["messages"])

@pytest.mark.asyncio
async def test_metrics_operations(clean_test_db, sample_metrics_data):
    """Test metrics storage and retrieval operations"""
    manager = clean_test_db
    
    if manager.test_mode == "mock":
        metric_id = f"test_metric_{int(time.time())}"
        manager.test_data["metrics"][metric_id] = {
            "id": metric_id,
            **sample_metrics_data,
            "timestamp": time.time()
        }
        
        # Test data retrieval
        retrieved_metric = await manager.get_test_data("metrics", metric_id)
        assert retrieved_metric is not None
        assert retrieved_metric["metric_type"] == sample_metrics_data["metric_type"]
        assert retrieved_metric["cpu_usage"] == sample_metrics_data["cpu_usage"]

@pytest.mark.asyncio
async def test_workflow_operations(clean_test_db, sample_workflow_data):
    """Test workflow storage and retrieval operations"""
    manager = clean_test_db
    
    if manager.test_mode == "mock":
        workflow_id = f"test_workflow_{int(time.time())}"
        manager.test_data["workflows"][workflow_id] = {
            "id": workflow_id,
            "execution_id": f"exec_{workflow_id}",
            **sample_workflow_data,
            "started_at": time.time()
        }
        
        # Test data retrieval
        retrieved_workflow = await manager.get_test_data("workflows", workflow_id)
        assert retrieved_workflow is not None
        assert retrieved_workflow["name"] == sample_workflow_data["name"]
        assert retrieved_workflow["status"] == sample_workflow_data["status"]

@pytest.mark.asyncio
async def test_database_cleanup(test_db_manager):
    """Test database cleanup functionality"""
    manager, _ = test_db_manager
    
    # This test runs at the end to verify cleanup works
    cleanup_result = await manager.cleanup_test_database()
    
    assert cleanup_result["cleanup_completed"] is True
    assert cleanup_result["status"] in ["cleaned", "error"]

# CLI interface for running database tests
if __name__ == "__main__":
    async def main():
        print("Test Database Manager - CLI Interface")
        print("=" * 50)
        
        # Create test database manager
        test_mode = os.getenv('TEST_DB_MODE', 'mock')
        manager = TestDatabaseManager(test_mode=test_mode)
        
        try:
            # Setup test database
            print(f"Setting up test database in {test_mode} mode...")
            setup_result = await manager.setup_test_database()
            print(f"Setup result: {setup_result['status']}")
            
            # Verify database
            print("Verifying database integrity...")
            verification_result = await manager.verify_test_database()
            print(f"Verification: {verification_result['data_integrity']}")
            
            # Show database contents
            if test_mode == "mock":
                print("\nDatabase contents:")
                for table, data in manager.test_data.items():
                    print(f"  {table}: {len(data)} records")
            
            # Test basic operations
            print("\nTesting basic operations...")
            
            # Test customer operations
            if test_mode == "mock":
                test_customer = {
                    "email": "cli.test@example.com",
                    "name": "CLI Test Customer",
                    "company": "CLI Test Corp"
                }
                customer_id = f"cli_test_{int(time.time())}"
                manager.test_data["customers"][customer_id] = {
                    "id": customer_id,
                    **test_customer,
                    "created_at": time.time()
                }
                
                retrieved = await manager.get_test_data("customers", customer_id)
                print(f"Customer test: {'PASSED' if retrieved else 'FAILED'}")
            
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(f"Error during testing: {e}")
            return 1
        
        finally:
            # Cleanup
            print("Cleaning up test database...")
            cleanup_result = await manager.cleanup_test_database()
            print(f"Cleanup: {'SUCCESS' if cleanup_result['cleanup_completed'] else 'FAILED'}")
        
        return 0
    
    import sys
    sys.exit(asyncio.run(main()))