"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Bot, 
  MessageSquare, 
  Settings, 
  User,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  BarChart3,
  Calendar
} from 'lucide-react'

interface CustomerAgent {
  id: string
  name: string
  type: 'chatbot' | 'ai_agent' | 'workflow'
  status: 'active' | 'paused' | 'setup'
  conversations: number
  lastActivity: string
  performance: number
}

interface CustomerStats {
  totalAgents: number
  activeConversations: number
  totalInteractions: number
  satisfaction: number
}

export default function CustomerDashboard() {
  const [customerEmail, setCustomerEmail] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [agents, setAgents] = useState<CustomerAgent[]>([])
  const [stats, setStats] = useState<CustomerStats>({
    totalAgents: 0,
    activeConversations: 0,
    totalInteractions: 0,
    satisfaction: 0
  })
  const [loading, setLoading] = useState(false)

  // Simple customer authentication
  const handleLogin = async () => {
    if (!customerEmail) {
      alert('Please enter your email')
      return
    }

    setLoading(true)
    try {
      // In production, implement proper authentication
      const response = await fetch('/api/customer/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: customerEmail })
      })

      if (response.ok) {
        setIsAuthenticated(true)
        loadCustomerData()
      } else {
        alert('Customer not found. Please contact support.')
      }
    } catch (error) {
      console.error('Authentication error:', error)
      // For demo purposes, allow any email
      setIsAuthenticated(true)
      loadCustomerData()
    } finally {
      setLoading(false)
    }
  }

  const loadCustomerData = async () => {
    setLoading(true)
    try {
      // Load customer agents
      const agentsResponse = await fetch(`/api/customer/agents?email=${customerEmail}`)
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json()
        setAgents(agentsData.agents || [])
        setStats(agentsData.stats || stats)
      } else {
        // Demo data if API not available
        setAgents([
          {
            id: '1',
            name: 'Customer Support Bot',
            type: 'chatbot',
            status: 'active',
            conversations: 156,
            lastActivity: '2 minutes ago',
            performance: 94
          },
          {
            id: '2',
            name: 'Order Processing Agent',
            type: 'ai_agent',
            status: 'active',
            conversations: 89,
            lastActivity: '1 hour ago',
            performance: 87
          }
        ])
        setStats({
          totalAgents: 2,
          activeConversations: 12,
          totalInteractions: 245,
          satisfaction: 4.6
        })
      }
    } catch (error) {
      console.error('Error loading customer data:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleAgent = async (agentId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active'
    
    try {
      const response = await fetch('/api/customer/agents/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentId, status: newStatus, customerEmail })
      })

      if (response.ok) {
        setAgents(prev => prev.map(agent => 
          agent.id === agentId ? { ...agent, status: newStatus as any } : agent
        ))
      }
    } catch (error) {
      console.error('Error toggling agent:', error)
      // For demo, update locally
      setAgents(prev => prev.map(agent => 
        agent.id === agentId ? { ...agent, status: newStatus as any } : agent
      ))
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <User className="h-6 w-6 text-primary" />
              <span>Customer Portal</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Email Address</label>
              <Input
                type="email"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                placeholder="Enter your email address"
                className="mt-1"
              />
            </div>
            <Button onClick={handleLogin} className="w-full" disabled={loading}>
              <User className="h-4 w-4 mr-2" />
              {loading ? 'Authenticating...' : 'Access My Dashboard'}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Enter your email to access your AI agents and analytics
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My AI Dashboard</h1>
            <p className="text-muted-foreground">Welcome back, {customerEmail}</p>
          </div>
          <Button variant="outline" onClick={() => setIsAuthenticated(false)}>
            Logout
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">My Agents</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalAgents}</div>
              <p className="text-xs text-muted-foreground">
                <CheckCircle className="h-3 w-3 inline mr-1 text-green-500" />
                All active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Chats</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeConversations}</div>
              <p className="text-xs text-muted-foreground">
                <Clock className="h-3 w-3 inline mr-1" />
                Live conversations
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Interactions</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalInteractions}</div>
              <p className="text-xs text-muted-foreground">
                <Calendar className="h-3 w-3 inline mr-1" />
                This month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Satisfaction</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.satisfaction}/5</div>
              <p className="text-xs text-muted-foreground">
                Average rating
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-4">
          <TabsList>
            <TabsTrigger value="agents">My Agents</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Your AI Agents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <Bot className="h-5 w-5 text-primary" />
                          <div className={`w-3 h-3 rounded-full ${
                            agent.status === 'active' ? 'bg-green-500' :
                            agent.status === 'paused' ? 'bg-yellow-500' : 'bg-gray-500'
                          }`} />
                        </div>
                        <div>
                          <h4 className="font-medium">{agent.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {agent.type} • {agent.conversations} conversations • {agent.performance}% performance
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Last active: {agent.lastActivity}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                          {agent.status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleAgent(agent.id, agent.status)}
                        >
                          {agent.status === 'active' ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </Button>
                        <Button size="sm" variant="outline">
                          Configure
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {agents.map((agent) => (
                      <div key={agent.id} className="flex justify-between items-center">
                        <span className="text-sm">{agent.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full" 
                              style={{ width: `${agent.performance}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{agent.performance}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Peak Hours</span>
                      <span className="font-medium">2PM - 4PM</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Avg Response Time</span>
                      <span className="font-medium">0.8s</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Resolution Rate</span>
                      <span className="font-medium">92%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Customer Retention</span>
                      <span className="font-medium">87%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-muted-foreground">Get notified of agent activities</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Configure
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">API Access</h4>
                    <p className="text-sm text-muted-foreground">Manage your API keys</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Manage
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Billing</h4>
                    <p className="text-sm text-muted-foreground">View usage and billing</p>
                  </div>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}