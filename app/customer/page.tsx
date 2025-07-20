'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Calendar,
  DollarSign,
  MessageSquare,
  FileText,
  Settings,
  Download,
  Eye
} from 'lucide-react'

interface CustomerProject {
  id: string
  serviceType: string
  status: string
  phase: string
  progress: number
  startDate: string
  estimatedCompletion: string
  assignedAgents: string[]
  lastUpdate: string
  description: string
}

interface Invoice {
  id: string
  amount: number
  status: string
  dueDate: string
  description: string
  downloadUrl?: string
}

interface Appointment {
  id: string
  type: string
  date: string
  time: string
  status: string
  meetingLink?: string
}

export default function CustomerDashboard() {
  const [projects, setProjects] = useState<CustomerProject[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [customerInfo, setCustomerInfo] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    totalProjects: 3,
    activeProjects: 2,
    totalSpent: 15000
  })

  useEffect(() => {
    // Mock data - replace with real API calls
    setProjects([
      {
        id: 'PROJ-001',
        serviceType: 'AI Chatbot',
        status: 'in_progress',
        phase: 'development',
        progress: 75,
        startDate: '2025-01-15',
        estimatedCompletion: '2025-01-22',
        assignedAgents: ['Development Team', 'QA Team'],
        lastUpdate: '2 hours ago',
        description: 'Custom AI chatbot for customer support with multilingual capabilities'
      },
      {
        id: 'PROJ-002',
        serviceType: 'Workflow Automation',
        status: 'testing',
        phase: 'quality_assurance',
        progress: 90,
        startDate: '2025-01-10',
        estimatedCompletion: '2025-01-20',
        assignedAgents: ['Automation Team'],
        lastUpdate: '1 day ago',
        description: 'Automated order processing and inventory management system'
      },
      {
        id: 'PROJ-003',
        serviceType: 'AI Agent',
        status: 'completed',
        phase: 'delivered',
        progress: 100,
        startDate: '2024-12-01',
        estimatedCompletion: '2024-12-15',
        assignedAgents: ['AI Team', 'Integration Team'],
        lastUpdate: '1 week ago',
        description: 'Intelligent customer service agent with CRM integration'
      }
    ])

    setInvoices([
      {
        id: 'INV-001',
        amount: 5000,
        status: 'paid',
        dueDate: '2025-01-15',
        description: 'AI Chatbot Development - Setup Fee',
        downloadUrl: '/invoices/INV-001.pdf'
      },
      {
        id: 'INV-002',
        amount: 3500,
        status: 'pending',
        dueDate: '2025-01-25',
        description: 'Workflow Automation - Monthly Service'
      },
      {
        id: 'INV-003',
        amount: 8000,
        status: 'paid',
        dueDate: '2024-12-15',
        description: 'AI Agent Development - Final Payment',
        downloadUrl: '/invoices/INV-003.pdf'
      }
    ])

    setAppointments([
      {
        id: 'APT-001',
        type: 'Project Review',
        date: '2025-01-22',
        time: '14:00',
        status: 'scheduled',
        meetingLink: 'https://meet.consulting.sa/room/apt-001'
      },
      {
        id: 'APT-002',
        type: 'Technical Consultation',
        date: '2025-01-25',
        time: '10:00',
        status: 'scheduled'
      }
    ])
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'in_progress':
      case 'testing':
      case 'scheduled':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      'completed': 'default',
      'in_progress': 'secondary',
      'testing': 'outline',
      'paid': 'default',
      'pending': 'destructive',
      'scheduled': 'secondary'
    } as const

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
        {status.replace('_', ' ')}
      </Badge>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, {customerInfo.name}</h1>
          <p className="text-gray-600 mt-2">Track your projects and manage your account</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customerInfo.activeProjects}</div>
              <p className="text-xs text-muted-foreground">
                {customerInfo.totalProjects} total projects
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Investment</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${customerInfo.totalSpent.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Across all projects
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Next Appointment</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Jan 22</div>
              <p className="text-xs text-muted-foreground">
                Project Review at 2:00 PM
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="projects" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger value="invoices">Invoices</TabsTrigger>
            <TabsTrigger value="appointments">Appointments</TabsTrigger>
            <TabsTrigger value="support">Support</TabsTrigger>
          </TabsList>

          {/* Projects Tab */}
          <TabsContent value="projects" className="space-y-6">
            <div className="space-y-6">
              {projects.map((project) => (
                <Card key={project.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center space-x-2">
                          {getStatusIcon(project.status)}
                          <span>{project.id} - {project.serviceType}</span>
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {project.description}
                        </CardDescription>
                      </div>
                      {getStatusBadge(project.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Progress Bar */}
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Progress ({project.phase})</span>
                          <span>{project.progress}%</span>
                        </div>
                        <Progress value={project.progress} className="h-2" />
                      </div>

                      {/* Project Details */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Started:</span>
                          <div className="font-medium">{project.startDate}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Est. Completion:</span>
                          <div className="font-medium">{project.estimatedCompletion}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Last Update:</span>
                          <div className="font-medium">{project.lastUpdate}</div>
                        </div>
                      </div>

                      {/* Assigned Teams */}
                      <div>
                        <span className="text-sm text-gray-600">Assigned Teams:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {project.assignedAgents.map((agent, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {agent}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-2 pt-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          <MessageSquare className="h-4 w-4 mr-2" />
                          Contact Team
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Invoices Tab */}
          <TabsContent value="invoices" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Invoices & Billing</CardTitle>
                <CardDescription>
                  View and manage your invoices and payments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {invoices.map((invoice) => (
                    <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(invoice.status)}
                        <div>
                          <h3 className="font-semibold">{invoice.id}</h3>
                          <p className="text-sm text-gray-600">{invoice.description}</p>
                          <p className="text-xs text-gray-500">Due: {invoice.dueDate}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">${invoice.amount.toLocaleString()}</div>
                        <div className="flex items-center space-x-2 mt-2">
                          {getStatusBadge(invoice.status)}
                          {invoice.downloadUrl && (
                            <Button variant="outline" size="sm">
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Appointments Tab */}
          <TabsContent value="appointments" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Appointments</CardTitle>
                <CardDescription>
                  Manage your scheduled meetings and consultations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {appointments.map((appointment) => (
                    <div key={appointment.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <Calendar className="h-8 w-8 text-blue-500" />
                        <div>
                          <h3 className="font-semibold">{appointment.type}</h3>
                          <p className="text-sm text-gray-600">
                            {appointment.date} at {appointment.time}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(appointment.status)}
                        {appointment.meetingLink && (
                          <Button size="sm">
                            Join Meeting
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Support Tab */}
          <TabsContent value="support" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Contact Support</CardTitle>
                  <CardDescription>
                    Get help with your projects and services
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Start Live Chat
                  </Button>
                  <Button variant="outline" className="w-full">
                    <Calendar className="h-4 w-4 mr-2" />
                    Schedule Call
                  </Button>
                  <Button variant="outline" className="w-full">
                    <FileText className="h-4 w-4 mr-2" />
                    Submit Ticket
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Resources</CardTitle>
                  <CardDescription>
                    Documentation and helpful resources
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <a href="#" className="block text-blue-600 hover:underline">
                      📚 User Documentation
                    </a>
                    <a href="#" className="block text-blue-600 hover:underline">
                      🎥 Video Tutorials
                    </a>
                    <a href="#" className="block text-blue-600 hover:underline">
                      ❓ FAQ
                    </a>
                    <a href="#" className="block text-blue-600 hover:underline">
                      🔧 API Documentation
                    </a>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}