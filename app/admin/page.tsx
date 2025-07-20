'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Users, 
  DollarSign, 
  Calendar,
  Bot,
  Settings,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'idle' | 'error'
  tasksCompleted: number
  currentTask?: string
  lastActivity: string
}

interface Project {
  id: string
  customerEmail: string
  serviceType: string
  status: string
  phase: string
  progress: number
  assignedAgents: string[]
  createdAt: string
  estimatedCompletion: string
}

export default function AdminDashboard() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [metrics, setMetrics] = useState({
    totalProjects: 0,
    activeProjects: 0,
    completedProjects: 0,
    totalRevenue: 0,
    activeAgents: 0,
    avgCompletionTime: '5.2 days'
  })

  useEffect(() => {
    // Mock data - replace with real API calls
    setAgents([
      {
        id: 'root-1',
        name: 'Root Agent',
        type: 'orchestrator',
        status: 'active',
        tasksCompleted: 45,
        currentTask: 'Orchestrating project PROJ-001',
        lastActivity: '2 minutes ago'
      },
      {
        id: 'acc-1',
        name: 'Accountant Agent',
        type: 'financial',
        status: 'active',
        tasksCompleted: 23,
        currentTask: 'Processing invoice INV-20250120-001',
        lastActivity: '5 minutes ago'
      },
      {
        id: 'cal-1',
        name: 'Calendar Agent',
        type: 'scheduling',
        status: 'idle',
        tasksCompleted: 18,
        lastActivity: '1 hour ago'
      },
      {
        id: 'n8n-1',
        name: 'N8N Agent',
        type: 'automation',
        status: 'active',
        tasksCompleted: 67,
        currentTask: 'Deploying workflow for customer@example.com',
        lastActivity: '1 minute ago'
      },
      {
        id: 'sales-1',
        name: 'Sales Agent',
        type: 'customer_relations',
        status: 'active',
        tasksCompleted: 34,
        currentTask: 'Qualifying lead prospect@example.com',
        lastActivity: '3 minutes ago'
      }
    ])

    setProjects([
      {
        id: 'PROJ-001',
        customerEmail: 'customer1@example.com',
        serviceType: 'AI Chatbot',
        status: 'in_progress',
        phase: 'development',
        progress: 75,
        assignedAgents: ['root-1', 'n8n-1', 'acc-1'],
        createdAt: '2025-01-18',
        estimatedCompletion: '2025-01-22'
      },
      {
        id: 'PROJ-002',
        customerEmail: 'customer2@example.com',
        serviceType: 'Workflow Automation',
        status: 'testing',
        phase: 'quality_assurance',
        progress: 90,
        assignedAgents: ['root-1', 'n8n-1'],
        createdAt: '2025-01-15',
        estimatedCompletion: '2025-01-20'
      },
      {
        id: 'PROJ-003',
        customerEmail: 'customer3@example.com',
        serviceType: 'AI Agent',
        status: 'requirements_gathering',
        phase: 'discovery',
        progress: 25,
        assignedAgents: ['root-1', 'sales-1'],
        createdAt: '2025-01-19',
        estimatedCompletion: '2025-01-25'
      }
    ])

    setMetrics({
      totalProjects: 15,
      activeProjects: 8,
      completedProjects: 7,
      totalRevenue: 125000,
      activeAgents: 4,
      avgCompletionTime: '5.2 days'
    })
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'idle':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      'active': 'default',
      'idle': 'secondary',
      'error': 'destructive',
      'in_progress': 'default',
      'testing': 'secondary',
      'requirements_gathering': 'outline',
      'completed': 'default'
    } as const

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
        {status.replace('_', ' ')}
      </Badge>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Agent Control Center</h1>
          <p className="text-gray-600 mt-2">Monitor and manage your multi-agent system</p>
        </div>

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.activeProjects}</div>
              <p className="text-xs text-muted-foreground">
                +2 from last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${metrics.totalRevenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +15% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.activeAgents}/5</div>
              <p className="text-xs text-muted-foreground">
                All systems operational
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Completion</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.avgCompletionTime}</div>
              <p className="text-xs text-muted-foreground">
                -0.5 days from last month
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Agents Tab */}
          <TabsContent value="agents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Agent Status</CardTitle>
                <CardDescription>
                  Monitor the status and activity of all specialized agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(agent.status)}
                          <div>
                            <h3 className="font-semibold">{agent.name}</h3>
                            <p className="text-sm text-gray-600">{agent.type}</p>
                          </div>
                        </div>
                        <div className="hidden md:block">
                          {getStatusBadge(agent.status)}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{agent.tasksCompleted} tasks completed</div>
                        {agent.currentTask && (
                          <div className="text-xs text-gray-600 max-w-xs truncate">
                            {agent.currentTask}
                          </div>
                        )}
                        <div className="text-xs text-gray-500">{agent.lastActivity}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Projects Tab */}
          <TabsContent value="projects" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Active Projects</CardTitle>
                <CardDescription>
                  Track progress and manage ongoing customer projects
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {projects.map((project) => (
                    <div key={project.id} className="border rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-lg">{project.id}</h3>
                          <p className="text-gray-600">{project.customerEmail}</p>
                        </div>
                        <div className="text-right">
                          {getStatusBadge(project.status)}
                          <div className="text-sm text-gray-600 mt-1">
                            {project.serviceType}
                          </div>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span>Progress ({project.phase})</span>
                          <span>{project.progress}%</span>
                        </div>
                        <Progress value={project.progress} className="h-2" />
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div>
                          <span className="text-gray-600">Assigned Agents: </span>
                          <span className="font-medium">{project.assignedAgents.length}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Est. Completion: </span>
                          <span className="font-medium">{project.estimatedCompletion}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Agent Performance</CardTitle>
                  <CardDescription>Tasks completed by each agent</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {agents.map((agent) => (
                      <div key={agent.id} className="flex items-center justify-between">
                        <span className="text-sm font-medium">{agent.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${(agent.tasksCompleted / 70) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-600">{agent.tasksCompleted}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Project Status Distribution</CardTitle>
                  <CardDescription>Current project phases</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Development</span>
                      <span className="text-sm text-gray-600">1 project</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Testing</span>
                      <span className="text-sm text-gray-600">1 project</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Discovery</span>
                      <span className="text-sm text-gray-600">1 project</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
                <CardDescription>
                  Configure agent settings and system parameters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">Auto-scaling</h3>
                      <p className="text-sm text-gray-600">Automatically scale agents based on workload</p>
                    </div>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">Notification Settings</h3>
                      <p className="text-sm text-gray-600">Configure alerts and notifications</p>
                    </div>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">API Keys</h3>
                      <p className="text-sm text-gray-600">Manage service integrations</p>
                    </div>
                    <Button variant="outline" size="sm">Manage</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}