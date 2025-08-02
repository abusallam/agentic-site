# Design Document

## Overview

This design addresses two main issues:
1. **Container Separation & Nginx Configuration**: Proper separation between production and development containers with correct nginx proxy configuration
2. **UI Enhancement**: Modern styling improvements using shadcn/ui components and better theming

## Architecture Design

### Container Separation Strategy

#### Development Environment
- **Container Names**: All development containers use `-dev` suffix
  - `agentic-frontend-dev` (port 3001)
  - `agentic-backend-dev` (port 8001) 
  - `agentic-redis-dev` (port 6380)
  - `agentic-n8n-dev` (port 5679)
- **Network**: `agentic-dev-network`
- **Deployment Path**: `/opt/agentic-platform-dev`
- **Domain**: `dev.consulting.sa`

#### Production Environment  
- **Container Names**: Production containers use standard names
  - `agentic-frontend` (port 3000)
  - `agentic-backend` (port 8000)
  - `agentic-redis` (port 6379)
  - `agentic-n8n` (port 5678)
- **Network**: `agentic-network`
- **Deployment Path**: `/opt/agentic-platform`
- **Domain**: `consulting.sa`

### Nginx Configuration Design

#### Current Issue
The nginx configuration in `infrastructure/nginx/development.conf` has incorrect upstream definitions and proxy targets:

```nginx
# INCORRECT - Points to container names that don't exist in development
upstream frontend_dev {
    server 127.0.0.1:3001;  # Should work but frontend container runs on port 3000
}

location / {
    root /usr/share/nginx/html;  # WRONG - Serves static files instead of proxying
    try_files $uri $uri/ /index.html;
}
```

#### Proposed Solution

**New Development Nginx Configuration:**

```nginx
# Correct upstream definitions for development containers
upstream frontend_dev {
    server 127.0.0.1:3001;  # Development frontend container port
}

upstream backend_dev {
    server 127.0.0.1:8001;  # Development backend container port  
}

upstream n8n_dev {
    server 127.0.0.1:5679;  # Development n8n container port
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    # Frontend - Proxy to Next.js container instead of static files
    location / {
        proxy_pass http://frontend_dev;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Next.js specific headers
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_buffering off;
    }
    
    # API routes to backend
    location /api/ {
        proxy_pass http://backend_dev/;
        # ... proxy headers
    }
    
    # n8n routes  
    location /n8n/ {
        proxy_pass http://n8n_dev/;
        # ... proxy headers with WebSocket support
    }
}
```

### Docker Compose Updates

#### Development Container Configuration
Update `infrastructure/docker/docker-compose.development.yml`:

```yaml
services:
  frontend-dev:
    image: ${FRONTEND_IMAGE:-ghcr.io/consulting-sa/agentic-frontend:development}
    container_name: agentic-frontend-dev
    ports:
      - "3001:3000"  # Map to port 3001 for development
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
    networks:
      - agentic-dev-network

  backend-dev:
    image: ${BACKEND_IMAGE:-ghcr.io/consulting-sa/agentic-backend:development}  
    container_name: agentic-backend-dev
    ports:
      - "8001:8000"  # Map to port 8001 for development
    networks:
      - agentic-dev-network

networks:
  agentic-dev-network:
    driver: bridge
    name: agentic-dev-network
```

## UI Enhancement Design

### Current UI Issues Analysis

Based on the project structure, the frontend uses Next.js with Tailwind CSS and shadcn/ui. Common issues to address:

1. **Inconsistent Theming**: Colors, spacing, typography not following design system
2. **Outdated Components**: Using basic HTML elements instead of shadcn/ui components  
3. **Poor Responsive Design**: Not optimized for mobile/tablet
4. **Accessibility Issues**: Missing ARIA labels, poor contrast ratios
5. **Loading States**: Missing skeleton loaders and loading indicators

### Design System Enhancement

#### Color Palette (Modern Dark/Light Theme)
```css
:root {
  /* Light theme */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;
  --accent: 210 40% 96%;
  --accent-foreground: 222.2 84% 4.9%;
  --muted: 210 40% 96%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
}

.dark {
  /* Dark theme */
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 84% 4.9%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 224.3 76.3% 94.1%;
}
```

#### Component Enhancement Strategy

**Priority Components to Upgrade:**

1. **Navigation Components**
   - Replace basic nav with shadcn/ui NavigationMenu
   - Add mobile-responsive hamburger menu
   - Implement breadcrumb navigation

2. **Form Components**
   - Replace HTML forms with shadcn/ui Form components
   - Add proper validation with react-hook-form
   - Implement loading states and error handling

3. **Data Display Components**
   - Replace tables with shadcn/ui DataTable
   - Add sorting, filtering, pagination
   - Implement skeleton loading states

4. **Interactive Components**
   - Replace buttons with shadcn/ui Button variants
   - Add proper hover/focus states
   - Implement loading spinners

5. **Layout Components**
   - Use shadcn/ui Card components for content sections
   - Implement proper spacing with Tailwind utilities
   - Add responsive grid layouts

### Implementation Strategy

#### Phase 1: Nginx Configuration Fix
1. Update nginx configuration file
2. Modify deployment script to use correct config
3. Test container connectivity
4. Verify all routes work properly

#### Phase 2: UI Component Audit
1. Scan existing components for upgrade opportunities
2. Identify custom components that need shadcn/ui integration
3. Create component migration plan
4. Set up design system documentation

#### Phase 3: Component Migration
1. Start with layout components (headers, navigation)
2. Migrate form components
3. Update data display components
4. Enhance interactive elements
5. Add loading states and error boundaries

#### Phase 4: Theme Enhancement
1. Implement proper dark/light mode toggle
2. Ensure consistent color usage
3. Improve typography hierarchy
4. Add proper spacing and layout
5. Test responsive design across devices

### File Structure for UI Enhancements

```
frontend/
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/            # Layout components
│   ├── forms/             # Form components  
│   └── data-display/      # Tables, cards, etc.
├── lib/
│   ├── utils.ts           # Utility functions
│   └── validations.ts     # Form validation schemas
├── styles/
│   ├── globals.css        # Global styles with CSS variables
│   └── components.css     # Component-specific styles
└── hooks/                 # Custom React hooks
```

## Success Metrics

### Technical Metrics
- ✅ Development site serves Next.js app instead of static files
- ✅ All API routes proxy correctly to backend container
- ✅ Container separation prevents production/dev conflicts
- ✅ SSL/HTTPS works properly in development

### UI/UX Metrics  
- ✅ Consistent design system across all pages
- ✅ Improved accessibility scores (WCAG 2.1 AA compliance)
- ✅ Responsive design works on mobile/tablet/desktop
- ✅ Loading states provide better user feedback
- ✅ Dark/light theme toggle works seamlessly

## Risk Mitigation

### Technical Risks
- **Container Port Conflicts**: Use different ports for dev/prod
- **Nginx Configuration Errors**: Test config before applying
- **SSL Certificate Issues**: Provide fallback to HTTP for dev

### UI Enhancement Risks
- **Breaking Changes**: Implement changes incrementally
- **Design Inconsistencies**: Create component library first
- **Performance Impact**: Monitor bundle size during migration