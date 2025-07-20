#!/usr/bin/env python3
"""
Database setup script for the Customer Journey Agent
This script creates the necessary tables in Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

def setup_database():
    """Set up the database tables in Supabase"""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read the SQL schema file
        schema_path = "agent/database_schema.sql" if os.path.exists("agent/database_schema.sql") else "database_schema.sql"
        with open(schema_path, "r") as f:
            sql_commands = f.read()
        
        # Split SQL commands by semicolon and execute each one
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        print(f"📝 Executing {len(commands)} SQL commands...")
        
        for i, command in enumerate(commands, 1):
            if command:
                try:
                    # Use the REST API to execute SQL
                    result = supabase.rpc('exec_sql', {'sql': command}).execute()
                    print(f"✅ Command {i}/{len(commands)} executed successfully")
                except Exception as e:
                    print(f"⚠️  Command {i} failed (might already exist): {str(e)[:100]}...")
        
        print("🎉 Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def test_database():
    """Test database connection and basic operations"""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test basic operations
        print("🧪 Testing database operations...")
        
        # Test 1: Check if tables exist
        try:
            result = supabase.table('customers').select('*').limit(1).execute()
            print("✅ Customers table accessible")
        except Exception as e:
            print(f"❌ Customers table error: {e}")
        
        try:
            result = supabase.table('workflows').select('*').limit(1).execute()
            print("✅ Workflows table accessible")
        except Exception as e:
            print(f"❌ Workflows table error: {e}")
        
        try:
            result = supabase.table('sessions').select('*').limit(1).execute()
            print("✅ Sessions table accessible")
        except Exception as e:
            print(f"❌ Sessions table error: {e}")
        
        try:
            result = supabase.table('payments').select('*').limit(1).execute()
            print("✅ Payments table accessible")
        except Exception as e:
            print(f"❌ Payments table error: {e}")
        
        print("🎉 Database test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up database...")
    setup_success = setup_database()
    
    if setup_success:
        print("\n🧪 Testing database...")
        test_database()
    else:
        print("❌ Database setup failed")