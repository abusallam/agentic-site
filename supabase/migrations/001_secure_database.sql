-- Enhanced security for the multi-agent system database
-- Run this in your Supabase SQL editor

-- Create customers table with enhanced security
CREATE TABLE IF NOT EXISTS customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    requirements JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'new',
    stripe_customer_id VARCHAR(255),
    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table for tracking customer projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_code VARCHAR(50) UNIQUE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'requirements_gathering',
    phase VARCHAR(50) DEFAULT 'discovery',
    progress INTEGER DEFAULT 0,
    requirements JSONB DEFAULT '{}',
    assigned_agents TEXT[] DEFAULT '{}',
    estimated_completion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    service_type VARCHAR(100) NOT NULL,
    deployment_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    config JSONB DEFAULT '{}',
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sessions table for live agent handoffs
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    room_name VARCHAR(255) NOT NULL,
    session_type VARCHAR(50) DEFAULT 'consultation',
    status VARCHAR(50) DEFAULT 'active',
    agent_email VARCHAR(255),
    transcript JSONB DEFAULT '[]',
    requirements_extracted JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    stripe_payment_intent_id VARCHAR(255),
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) DEFAULT 'pending',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    amount INTEGER NOT NULL,
    tax_amount INTEGER DEFAULT 0,
    total_amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) DEFAULT 'pending',
    due_date DATE,
    line_items JSONB DEFAULT '[]',
    stripe_invoice_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    appointment_type VARCHAR(100) NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status VARCHAR(50) DEFAULT 'scheduled',
    meeting_link VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agent_tasks table for tracking agent work
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'assigned',
    result JSONB DEFAULT '{}',
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_conversations table
CREATE TABLE IF NOT EXISTS chat_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    conversation_id VARCHAR(255) NOT NULL,
    messages JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    handoff_requested BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_auth_user_id ON customers(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_projects_customer_id ON projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_workflows_customer_id ON workflows(customer_id);
CREATE INDEX IF NOT EXISTS idx_workflows_project_id ON workflows(project_id);
CREATE INDEX IF NOT EXISTS idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_customer_id ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments(customer_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_project_id ON agent_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_customer_id ON chat_conversations(customer_id);

-- Enable Row Level Security (RLS)
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_conversations ENABLE ROW LEVEL SECURITY;

-- Create security policies

-- Customers table policies
CREATE POLICY "Users can view their own customer record" ON customers
    FOR SELECT USING (auth.uid() = auth_user_id OR auth.role() = 'service_role');

CREATE POLICY "Users can update their own customer record" ON customers
    FOR UPDATE USING (auth.uid() = auth_user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage all customers" ON customers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Authenticated users can create customer records" ON customers
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- Projects table policies
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = projects.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Service role can manage all projects" ON projects
    FOR ALL USING (auth.role() = 'service_role');

-- Workflows table policies
CREATE POLICY "Users can view their workflows" ON workflows
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = workflows.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Service role can manage all workflows" ON workflows
    FOR ALL USING (auth.role() = 'service_role');

-- Sessions table policies
CREATE POLICY "Users can view their sessions" ON sessions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = sessions.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Service role can manage all sessions" ON sessions
    FOR ALL USING (auth.role() = 'service_role');

-- Payments table policies
CREATE POLICY "Users can view their payments" ON payments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = payments.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Service role can manage all payments" ON payments
    FOR ALL USING (auth.role() = 'service_role');

-- Invoices table policies
CREATE POLICY "Users can view their invoices" ON invoices
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = invoices.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Service role can manage all invoices" ON invoices
    FOR ALL USING (auth.role() = 'service_role');

-- Appointments table policies
CREATE POLICY "Users can view their appointments" ON appointments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = appointments.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        )
    );

CREATE POLICY "Users can update their appointments" ON appointments
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = appointments.customer_id 
            AND auth.uid() = customers.auth_user_id
        )
    );

CREATE POLICY "Service role can manage all appointments" ON appointments
    FOR ALL USING (auth.role() = 'service_role');

-- Agent tasks policies (admin only)
CREATE POLICY "Only service role can access agent tasks" ON agent_tasks
    FOR ALL USING (auth.role() = 'service_role');

-- Chat conversations policies
CREATE POLICY "Users can view their chat conversations" ON chat_conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM customers 
            WHERE customers.id = chat_conversations.customer_id 
            AND (auth.uid() = customers.auth_user_id OR auth.role() = 'service_role')
        ) OR auth.role() = 'service_role'
    );

CREATE POLICY "Service role can manage all chat conversations" ON chat_conversations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Anonymous users can create chat conversations" ON chat_conversations
    FOR INSERT WITH CHECK (true);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_conversations_updated_at BEFORE UPDATE ON chat_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create admin user role for agent access
-- This should be done through Supabase dashboard or with proper service role key
-- INSERT INTO auth.users (id, email, role) VALUES (gen_random_uuid(), 'admin@consulting.sa', 'service_role');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE ON customers TO authenticated;
GRANT SELECT ON projects, workflows, sessions, payments, invoices, appointments TO authenticated;
GRANT INSERT, UPDATE ON appointments TO authenticated;
GRANT INSERT ON chat_conversations TO anon;
GRANT SELECT, INSERT, UPDATE ON chat_conversations TO authenticated;

-- Service role gets full access
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;