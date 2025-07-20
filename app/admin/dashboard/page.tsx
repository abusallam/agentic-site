"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Users, 
  MessageSquare, 
  Activity, 
  Settings, 
  Eye,
  Shield,
  BarChart3,
  Clock,
  AlertCircle,
  CheckCircle,
  TrendingUp,
  Server
} from 'lucide-react'

interface AdminStats {
  totalCustomers: number
  activeAgents: number
  totalConversations: number
  systemHealth: 'healthy' | 'warning' | 'error'
}

interface AgentActivity {
  id: string
  name: string
  status: 'active' | 'idle' | 'offline'
  conversations: number
  lastActivity: string
}

interface CustomerSession {
  id: string
  email: string
  status: 'active' | 'waiting' | 'completed'
  agent: string
  startTime: string
  duration: string
}

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [stats, setStats] = useState<AdminStats>({
    totalCustomers: 0,
    activeAgents: 0,
    totalConversations: 0,
    systemHealth: 'healthy'
  })
  const [agents, setAgents] = useState<AgentActivity[]>([])
  const [sessions, setSessions] = useState<CustomerSession[]>([])
  const [loading, setLoading] = useState(false)

  // Simple authentication (in production, use proper auth)
  const handleLogin = () => {
    if (password === 'admin123') {
      setIsAuthenticated(true)
      loadDashboardData()
    } else {
      alert('Invalid password')
    }
  }

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // Load stats from backend
      const statsResponse = await fetch('/api/admin/stats')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Load agent activities
      const agentsResponse = await fetch('/api/admin/agents')
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json()
        setAgents(agentsData)
      }

      // Load customer sessions
      const sessionsResponse = await fetch('/api/admin/customers')
      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json()
        setSessions(sessionsData)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      const interval = setInterval(loadDashboardData, 30000) // Refresh every 30 seconds
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <Shield className="h-6 w-6 text-primary" />
              <span>Admin Access</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                placeholder="Enter admin password"
                className="mt-1"
              />
            </div>
            <Button onClick={handleLogin} className="w-full">
              <Shield className="h-4 w-4 mr-2" />
              Login to Admin Panel
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Default password: admin123
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-muted-foreground">Monitor agents, customers, and system health</p>
          </div>
          <Button variant="outline" onClick={() => setIsAuthenticated(false)}>
            Logout
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalCustomers}</div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3 inline mr-1" />
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeAgents}</div>
              <p className="text-xs text-muted-foreground">
                <CheckCircle className="h-3 w-3 inline mr-1 text-green-500" />
                All systems operational
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conversations</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalConversations}</div>
              <p className="text-xs text-muted-foreground">
                <Clock className="h-3 w-3 inline mr-1" />
                24h activity
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Badge variant={stats.systemHealth === 'healthy' ? 'default' : 'destructive'}>
                  {stats.systemHealth === 'healthy' ? (
                    <CheckCircle className="h-3 w-3 mr-1" />
                  ) : (
                    <AlertCircle className="h-3 w-3 mr-1" />
                  )}
                  {stats.systemHealth}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                All services running
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-4">
          <TabsList>
            <TabsTrigger value="agents">Agent Activity</TabsTrigger>
            <TabsTrigger value="customers">Customer Sessions</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Agent Activity Monitor</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${
                          agent.status === 'active' ? 'bg-green-500' :
                          agent.status === 'idle' ? 'bg-yellow-500' : 'bg-red-500'
                        }`} />
                        <div>
                          <h4 className="font-medium">{agent.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {agent.conversations} conversations • Last active: {agent.lastActivity}
                          </p>
                        </div>
                      </div>
                      <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                        {agent.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="customers" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Customer Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sessions.map((session) => (
                    <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <Eye className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <h4 className="font-medium">{session.email}</h4>
                          <p className="text-sm text-muted-foreground">
                            Agent: {session.agent} • Duration: {session.duration}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={
                          session.status === 'active' ? 'default' :
                          session.status === 'waiting' ? 'secondary' : 'outline'
                        }>
                          {session.status}
                        </Badge>
                        <Button size="sm" variant="outline">
                          View Details
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
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Response Time</span>
                      <span className="font-medium">1.2s avg</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Success Rate</span>
                      <span className="font-medium">98.5%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Customer Satisfaction</span>
                      <span className="font-medium">4.8/5</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System Resources</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>CPU Usage</span>
                      <span className="font-medium">45%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Memory Usage</span>
                      <span className="font-medium">62%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>API Calls/min</span>
                      <span className="font-medium">1,247</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>System Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Auto-refresh Dashboard</h4>
                    <p className="text-sm text-muted-foreground">Refresh data every 30 seconds</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Enabled
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-muted-foreground">Get notified of system alerts</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Configure
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Backup Settings</h4>
                    <p className="text-sm text-muted-foreground">Automatic daily backups</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Manage
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