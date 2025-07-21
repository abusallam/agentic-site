# consulting.sa Website (المستشار.السعودية)

[![Deployed on Coolify](https://img.shields.io/badge/Deployed%20on-Coolify-blue?style=for-the-badge&logo=docker)](https://consulting.sa)
[![Built with Next.js](https://img.shields.io/badge/Built%20with-Next.js-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

Professional AI consulting services and SaaS solutions website for **consulting.sa** (المستشار.السعودية), specializing in artificial intelligence, chatbots, AI agents, and digital transformation services in Saudi Arabia.

## 🚀 Live Website

Visit our website: **[https://consulting.sa](https://consulting.sa)**

## 📋 About

**consulting.sa** (المستشار.السعودية) provides cutting-edge AI consulting services including:

- **AI Strategy & Implementation** - Custom AI solutions for businesses
- **Chatbot Development** - Intelligent conversational AI systems
- **AI Agent Creation** - Autonomous AI agents for automation
- **Digital Transformation** - Modernizing business processes with AI
- **SaaS Solutions** - Scalable software-as-a-service platforms

## 🛠️ Tech Stack

### Core Technologies
- **Framework**: Next.js 15.4.1 with App Router
- **Language**: TypeScript 5.7.3
- **Styling**: Tailwind CSS 3.4.17
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React
- **Database**: Supabase
- **Package Manager**: npm

### Development Tools
- **Code Quality**: ESLint, Prettier, Husky
- **Performance**: Bundle Analyzer, Image Optimization
- **Deployment**: Docker, Vercel
- **Monitoring**: Health Checks, Error Boundaries

## 🏗️ Project Structure

```
├── app/                    # Next.js app directory (App Router)
│   ├── about/             # About page
│   ├── api/               # API routes
│   │   └── health/        # Health check endpoint
│   ├── auth/              # Authentication pages
│   ├── consulting/        # Consulting services page
│   ├── contact/           # Contact page
│   ├── docs/              # Documentation pages
│   ├── documentation/     # API documentation
│   ├── privacy-policy/    # Privacy policy page
│   ├── services/          # Services pages
│   ├── test-auth/         # Authentication testing
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── loading.tsx        # Global loading UI
│   ├── error.tsx          # Global error UI
│   └── page.tsx           # Home page
├── components/            # Reusable React components
│   ├── ui/               # Shadcn/ui component library
│   ├── consulting/       # Consulting-specific components
│   ├── *-enhanced.tsx    # Enhanced feature components
│   └── *.tsx             # Other components
├── lib/                  # Utility functions and configurations
│   ├── brand.ts          # Brand configuration
│   ├── i18n-enhanced.tsx # Internationalization
│   ├── supabase.ts       # Supabase client
│   └── utils.ts          # Utility functions
├── hooks/                # Custom React hooks
├── public/               # Static assets
│   ├── *.webp           # Optimized images
│   └── *.svg            # Vector graphics
├── styles/               # Additional styles
│   └── animations.css   # Custom animations
├── docs/                 # Project documentation
├── scripts/              # Build and deployment scripts
├── .github/              # GitHub workflows and templates
└── Docker files          # Container configuration
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ (LTS recommended)
- **npm** 9+ or **yarn** 1.22+
- **Git** for version control
- **Docker** (optional, for containerized deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/consulting-sa/website.git
   cd website
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Configure your environment variables:
   ```env
   # Supabase Configuration
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # Contact Configuration
   NEXT_PUBLIC_CONTACT_EMAIL=asim@consulting.sa
   
   # Analytics (optional)
   NEXT_PUBLIC_GA_ID=your_google_analytics_id
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📜 Available Scripts

### Development
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build optimized production bundle
- `npm run start` - Start production server
- `npm run clean` - Clean build artifacts and cache

### Code Quality
- `npm run lint` - Run ESLint with auto-fix
- `npm run lint:check` - Check linting without fixing
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking

### Analysis & Testing
- `npm run analyze` - Analyze bundle size with webpack-bundle-analyzer
- `npm run test` - Run tests (placeholder for future implementation)

### Docker Deployment
- `npm run docker:build` - Build Docker image
- `npm run docker:run` - Run Docker container
- `npm run docker:compose` - Run with Docker Compose

## 🌐 Features

### Core Features
- **🎨 Modern Design** - Clean, professional UI with glass morphism effects
- **📱 Responsive Design** - Mobile-first approach with Tailwind CSS
- **🌙 Dark/Light Mode** - Seamless theme switching with next-themes
- **🌍 Internationalization** - Multi-language support (Arabic/English)
- **⚡ Performance Optimized** - Image optimization, code splitting, lazy loading
- **♿ Accessibility** - WCAG 2.1 AA compliant components
- **🔒 Security** - Security headers, CSP, and best practices

### Technical Features
- **🚀 App Router** - Next.js 13+ App Router with server components
- **📊 SEO Optimized** - Meta tags, Open Graph, structured data
- **🎯 Type Safety** - Full TypeScript implementation
- **🔄 Error Handling** - Comprehensive error boundaries and fallbacks
- **📈 Analytics Ready** - Google Analytics integration
- **🐳 Docker Ready** - Multi-stage Docker build for production

### Business Features
- **💼 Consulting Services** - Comprehensive AI consulting showcase
- **📝 Privacy Policy** - GDPR-compliant privacy documentation
- **📞 Contact Forms** - Integrated contact and inquiry forms
- **🎯 Service Pages** - Detailed AI services and solutions
- **📚 Documentation** - API and integration documentation

## 🔧 Configuration

### Environment Variables

#### **Core Application Variables**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes | - |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | Yes | - |
| `NEXT_PUBLIC_CONTACT_EMAIL` | Contact email address | No | asim@consulting.sa |
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | No | - |
| `ANALYZE` | Enable bundle analyzer | No | false |

#### **Production Environment Variables**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NODE_ENV` | Environment mode | Yes | production |
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry | No | 1 |
| `NEXT_PUBLIC_SITE_URL` | Public site URL | Yes | http://217.79.255.54 |
| `NEXT_PUBLIC_ADMIN_URL` | Admin interface URL | Yes | http://217.79.255.54:8953 |
| `FORCE_HTTPS` | Force HTTPS redirects | No | false |

#### **AI Services Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | No | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | No | - |
| `GEMINI_API_KEY` | Google Gemini API key | No | - |

#### **Payment Integration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `STRIPE_SECRET_KEY` | Stripe secret key | No | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | No | - |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | No | - |

#### **Communication Services**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LIVEKIT_URL` | Livekit server URL | No | - |
| `LIVEKIT_API_KEY` | Livekit API key | No | - |
| `LIVEKIT_API_SECRET` | Livekit API secret | No | - |

#### **Workflow Automation**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `N8N_URL` | n8n instance URL | No | - |
| `N8N_BASE_URL` | n8n base URL | No | - |
| `N8N_API_KEY` | n8n API key | No | - |

#### **MCP Server Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MCP_SERVER_URL` | MCP server URL | No | http://localhost:8000 |
| `MCP_SERVER_PORT` | MCP server port | No | 8000 |
| `N8N_MCP_PORT` | n8n MCP port | No | 8003 |
| `GITHUB_TOKEN` | GitHub token for MCP | No | - |

#### **Backend Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ADK_AGENT_PORT` | Agent server port | No | 8953 |
| `ADK_LOG_LEVEL` | Logging level | No | INFO |
| `PYTHONPATH` | Python path | No | /app/agent |

#### **Docker Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `COMPOSE_PROJECT_NAME` | Docker Compose project name | No | agentic-site |
| `COMPOSE_HTTP_TIMEOUT` | HTTP timeout for Compose | No | 120 |
| `DOMAIN` | Domain name | No | 217.79.255.54 |

#### **Health Check Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `HEALTH_CHECK_ENABLED` | Enable health checks | No | true |
| `HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | No | 30 |

### Brand Configuration

Customize your brand in `lib/brand.ts`:

```typescript
export const brandConfig = {
  name: "consulting.sa",
  nameArabic: "المستشار.السعودية",
  tagline: "AI Consulting & Digital Transformation",
  taglineArabic: "استشارات الذكاء الاصطناعي والتحول الرقمي",
  description: "Professional AI consulting services and SaaS solutions",
  url: "https://consulting.sa",
  logo: {
    image: "/logo.webp",
    width: 40,
    height: 40,
  },
  contact: {
    email: "asim@consulting.sa",
    phone: "+966-XXX-XXXX",
  },
  social: {
    linkedin: "https://linkedin.com/company/consulting-sa",
    twitter: "https://twitter.com/consultingsa",
  },
}
```

### Tailwind Configuration

The project uses a custom Tailwind configuration with:
- **Custom Colors** - Brand-specific color palette
- **Typography** - Inter and Cairo fonts for multilingual support
- **Animations** - Custom keyframes and transitions
- **Components** - Utility classes for common patterns

## 🚢 Deployment

### Production VPS Deployment (Current) ✅

**Status**: Successfully deployed on production VPS  
**Server**: 217.79.255.54  
**Architecture**: Docker Compose multi-service deployment  

#### **Current Deployment Status**
- **Frontend (Next.js)**: ✅ Running on port 3911
- **Backend (Python Agent)**: ✅ Running on port 8953
- **Security**: ✅ UFW Firewall + Fail2ban active
- **SSL Ready**: ✅ Port 443 configured for HTTPS
- **Management**: ✅ Automated scripts installed

#### **Access Points**
- **Next.js Frontend**: http://217.79.255.54:3911/
- **Python Backend**: http://217.79.255.54:8953/
- **SSH Access**: ssh root@217.79.255.54 (secured)

#### **VPS Specifications**
- **OS**: Debian 12 (Bookworm)
- **RAM**: 23GB
- **Storage**: 394GB
- **CPU**: Multi-core x86_64
- **Network**: 1Gbps connection

#### **Management Commands**
```bash
# Application status
/usr/local/bin/agentic-site-status.sh

# Restart application
/usr/local/bin/agentic-site-restart.sh

# View logs
cd /opt/docker-apps/production/agentic-site
docker compose logs -f

# Container management
docker compose ps                 # Check status
docker compose restart           # Restart services
docker compose down && docker compose up -d  # Full restart
```

#### **VPS Environment Configuration**

**🔑 VPS Access Credentials:**
```bash
# SSH Access
Host: 217.79.255.54
Username: root
Password: gt5qXy22aJ
Port: 22

# SSH Command
ssh root@217.79.255.54
```

**🌐 Service URLs:**
- **Frontend**: http://217.79.255.54/ (Next.js on port 3911)
- **HTTPS**: https://217.79.255.54/ (SSL enabled)
- **Backend**: http://217.79.255.54:8953/ (Python Agent)
- **Health Check**: http://217.79.255.54/health (Nginx health)

**📊 Current Deployment Status:**
- ✅ **Frontend Deployed**: Next.js running on port 3911
- ✅ **Backend Deployed**: Python agent on port 8953
- ✅ **SSL Configured**: Cloudflare SSL certificate installed
- ✅ **Nginx Proxy**: Reverse proxy configured
- ✅ **Docker Containers**: Multi-service deployment active
- ⚠️ **Health Endpoints**: Some API endpoints need configuration
- ✅ **Performance**: Excellent load times (0.4-0.6s average)

**🔧 Management Commands:**
```bash
# Check application status
/usr/local/bin/agentic-site-status.sh

# Restart application
/usr/local/bin/agentic-site-restart.sh

# View container logs
cd /opt/docker-apps/production/agentic-site
docker compose logs -f

# Container management
docker compose ps                 # Check status
docker compose restart           # Restart services
docker compose down && docker compose up -d  # Full restart
```

**📁 Deployment Structure:**
```
/opt/docker-apps/production/agentic-site/
├── docker-compose.yml           # Main compose file
├── .env                        # Environment variables
├── Dockerfile.frontend         # Next.js container
├── Dockerfile.backend          # Python agent container
├── app/                        # Next.js application
├── agent/                      # Python agent code
├── components/                 # React components
├── lib/                        # Utilities
└── docs/                       # Documentation
```

**🔒 SSL Certificate Information:**
- **Provider**: Cloudflare Origin SSL
- **Domain**: consulting.sa, www.consulting.sa
- **Certificate Path**: `/etc/nginx/ssl/consulting.sa/certificate.crt`
- **Private Key Path**: `/etc/nginx/ssl/consulting.sa/private.key`
- **Expires**: 2040-07-17 (15+ years validity)
- **Auto-renewal**: Not required (long expiry)

**🛡️ Security Configuration:**
- **Firewall**: UFW active with restricted ports
- **Fail2ban**: Active for SSH protection
- **SSL/TLS**: TLSv1.2 and TLSv1.3 enabled
- **Security Headers**: HSTS, XSS protection, frame options
- **Access Control**: Root access only, key-based auth recommended

See [VPS_CONFIGURATION.md](VPS_CONFIGURATION.md) for complete server documentation including:
- System specifications and software versions
- Network configuration and security settings
- Environment variables and service configuration
- Monitoring and maintenance procedures
- Backup and recovery strategies

### Vercel Deployment

1. **Connect your repository** to Vercel
2. **Configure environment variables** in Vercel dashboard
3. **Deploy** - Automatic deployments on push to main

### Docker Deployment (Local)

1. **Build the image**
   ```bash
   docker build -t agentic-site .
   ```

2. **Run the container**
   ```bash
   docker run -p 3000:3000 agentic-site
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose up --build
   ```

### Manual Deployment

1. **Build the project**
   ```bash
   npm run build
   ```

2. **Start the production server**
   ```bash
   npm start
   ```

## 📊 Performance Optimizations

### Image Optimization
- **WebP/AVIF formats** for modern browsers
- **Responsive images** with multiple sizes
- **Lazy loading** for better performance
- **Sharp** for server-side image processing

### Code Splitting
- **Automatic code splitting** by Next.js
- **Dynamic imports** for heavy components
- **Bundle analysis** with webpack-bundle-analyzer

### Caching Strategy
- **Static assets** cached for 1 year
- **API routes** with appropriate cache headers
- **Service worker** for offline functionality (future)

## 🔒 Security

### Headers
- **X-Frame-Options** - Prevent clickjacking
- **X-Content-Type-Options** - Prevent MIME sniffing
- **Referrer-Policy** - Control referrer information
- **Permissions-Policy** - Restrict browser features

### Content Security Policy
- **Strict CSP** for SVG content
- **Nonce-based** script execution
- **Trusted domains** for external resources

## 📱 Responsive Breakpoints

| Breakpoint | Size | Usage |
|------------|------|-------|
| `sm` | 640px+ | Small tablets |
| `md` | 768px+ | Tablets |
| `lg` | 1024px+ | Small desktops |
| `xl` | 1280px+ | Large desktops |
| `2xl` | 1536px+ | Extra large screens |

## 🧪 Testing

### Current Status
- **Unit Tests** - Not implemented (placeholder)
- **Integration Tests** - Not implemented (placeholder)
- **E2E Tests** - Not implemented (placeholder)

### Future Implementation
- **Jest** for unit testing
- **React Testing Library** for component testing
- **Playwright** for E2E testing

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run quality checks**
   ```bash
   npm run lint
   npm run type-check
   npm run format
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style

- **TypeScript** for all new code
- **Functional components** with hooks
- **Tailwind CSS** for styling
- **ESLint + Prettier** for code formatting
- **Conventional commits** for commit messages

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Configuration Guide](docs/configuration.md)** - Environment and settings
- **[API Reference](docs/api-reference.md)** - API endpoints documentation
- **[Style Guide](docs/style-guide.md)** - Design system and components
- **[i18n Guide](docs/i18n-guide.md)** - Internationalization setup

## 🐛 Troubleshooting

### Common Issues

1. **Build Errors**
   - Check Node.js version (18+ required)
   - Clear cache: `npm run clean`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

2. **Environment Variables**
   - Ensure `.env.local` exists and is configured
   - Restart development server after changes

3. **Docker Issues**
   - Check Docker daemon is running
   - Verify port 3000 is available
   - Check environment variables in docker-compose.yml

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

**Asim Abu Salam** - Lead Developer & AI Consultant
- **Email**: asim@consulting.sa
- **Website**: [consulting.sa](https://consulting.sa)
- **LinkedIn**: [consulting.sa](https://linkedin.com/company/consulting-sa)

For technical support or business inquiries, please reach out via email or through our website contact form.

## 🙏 Acknowledgments

### Technologies
- **[Next.js](https://nextjs.org/)** - React framework for production
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Radix UI](https://www.radix-ui.com/)** - Low-level UI primitives
- **[Lucide](https://lucide.dev/)** - Beautiful & consistent icons
- **[Supabase](https://supabase.com/)** - Open source Firebase alternative

### Inspiration
- **[Shadcn/ui](https://ui.shadcn.com/)** - Component design system
- **[Vercel](https://vercel.com/)** - Deployment and hosting platform
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety and developer experience

---

**Built with ❤️ by consulting.sa Team (المستشار.السعودية)**