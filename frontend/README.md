# 🎨 Frontend - Next.js Application

## 📋 Overview

The frontend is a modern Next.js 15.4.1 application built with TypeScript, Tailwind CSS, and React 19. It provides a comprehensive AI consulting platform interface with responsive design, internationalization, and production-ready optimizations.

**Framework**: Next.js 15.4.1 with App Router  
**Package Manager**: `npm`  
**Language**: TypeScript 5.7.3  
**Styling**: Tailwind CSS 3.4.17  
**Status**: ✅ Production Ready

## 🏗️ Architecture

```
frontend/
├── app/                        # Next.js App Router
│   ├── about/                 # About page
│   ├── admin/                 # Admin dashboard
│   ├── api/                   # API routes
│   │   ├── admin/            # Admin API endpoints
│   │   ├── agent/            # Agent API endpoints
│   │   ├── chat/             # Chat API
│   │   ├── customer/         # Customer API
│   │   ├── health/           # Health check endpoints
│   │   └── metrics/          # Metrics endpoint
│   ├── auth/                 # Authentication pages
│   ├── consulting/           # Consulting services
│   ├── contact/              # Contact page
│   ├── customer/             # Customer dashboard
│   ├── docs/                 # Documentation pages
│   ├── privacy-policy/       # Privacy policy
│   ├── services/             # Services overview
│   ├── test-auth/            # Authentication testing
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   ├── loading.tsx           # Loading UI
│   ├── error.tsx             # Error UI
│   └── page.tsx              # Home page
├── components/                # React components
│   ├── ui/                   # Shadcn/ui components
│   │   ├── button.tsx        # Button component
│   │   ├── card.tsx          # Card component
│   │   ├── input.tsx         # Input component
│   │   ├── calendar.tsx      # Calendar component
│   │   ├── chart.tsx         # Chart component
│   │   └── ...               # Other UI components
│   ├── chatbot/              # Chatbot components
│   ├── consulting/           # Consulting components
│   ├── features/             # Feature components
│   ├── layout/               # Layout components
│   ├── cta-section.tsx       # Call-to-action section
│   ├── error-boundary.tsx    # Error boundary
│   ├── lazy-image.tsx        # Lazy loading image
│   ├── performance-monitor.tsx # Performance monitoring
│   └── theme-provider-enhanced.tsx # Theme provider
├── lib/                      # Utilities and configurations
│   ├── brand.ts              # Brand configuration
│   ├── i18n.ts               # Internationalization
│   ├── i18n-enhanced.tsx     # Enhanced i18n components
│   ├── image-optimizer.ts    # Image optimization
│   ├── supabase.ts           # Supabase client
│   └── utils.ts              # Utility functions
├── hooks/                    # Custom React hooks
│   ├── use-mobile.tsx        # Mobile detection hook
│   └── use-toast.ts          # Toast notification hook
├── styles/                   # CSS files
│   ├── animations.css        # Animation styles
│   └── globals.css           # Global styles
├── public/                   # Static assets
│   ├── logo.webp             # Logo image
│   ├── bg1.webp              # Background image
│   ├── favicon.ico           # Favicon
│   └── ...                   # Other static assets
├── tests/                    # Frontend tests
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.ts        # Tailwind configuration
├── next.config.mjs           # Next.js configuration
├── components.json           # Shadcn/ui configuration
├── .eslintrc.json            # ESLint configuration
├── .prettierrc               # Prettier configuration
├── playwright.config.ts      # Playwright configuration
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (LTS recommended)
- **npm 9+** (comes with Node.js)

### Setup and Run

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   # Copy environment template (from project root)
   cp ../.env.example ../.env
   # Edit with your actual values
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   - Visit: [http://localhost:3000](http://localhost:3000)

## 📦 Package Management

### Dependencies

#### Core Framework
- **next@15.4.1** - React framework with App Router
- **react@19.0.0** - React library
- **react-dom@19.0.0** - React DOM renderer
- **typescript@5.7.3** - TypeScript language

#### Styling & UI
- **tailwindcss@3.4.17** - Utility-first CSS framework
- **@tailwindcss/typography** - Typography plugin
- **@radix-ui/react-*** - Headless UI primitives
- **lucide-react** - Icon library
- **next-themes** - Theme switching

#### Database & Auth
- **@supabase/supabase-js** - Supabase client
- **@supabase/ssr** - Server-side rendering support

#### Development Tools
- **eslint@9.18.0** - Code linting
- **prettier** - Code formatting
- **@types/*** - TypeScript type definitions

### Scripts

```bash
# Development
npm run dev              # Start development server
npm run build           # Build for production
npm run start           # Start production server
npm run clean           # Clean build artifacts

# Code Quality
npm run lint            # Run ESLint with auto-fix
npm run lint:check      # Check linting without fixing
npm run format          # Format code with Prettier
npm run format:check    # Check code formatting
npm run type-check      # Run TypeScript type checking

# Analysis
npm run analyze         # Analyze bundle size
```

## 🎨 Styling System

### Tailwind CSS Configuration

The project uses a custom Tailwind configuration with:

```typescript
// tailwind.config.ts
export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom brand colors
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        // ... other colors
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        arabic: ['Cairo', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('tailwindcss-animate'),
  ],
}
```

### Component Library

The project uses **shadcn/ui** components:

```bash
# Add new shadcn/ui component
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
```

### Custom Components

#### UI Components (`components/ui/`)
- **Button** - Customizable button with variants
- **Card** - Container component with header/content/footer
- **Input** - Form input with validation states
- **Calendar** - Date picker component
- **Chart** - Data visualization component

#### Feature Components
- **ChatbotWidget** - AI chatbot interface
- **CTASection** - Call-to-action sections
- **LazyImage** - Optimized image loading
- **ErrorBoundary** - Error handling wrapper

## 🌐 Internationalization (i18n)

### Language Support

- **English** (default)
- **Arabic** (العربية)

### Usage

```typescript
// In components
import { useTranslation } from '@/lib/i18n-enhanced'

export function MyComponent() {
  const { t, locale, setLocale } = useTranslation()
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <button onClick={() => setLocale('ar')}>
        العربية
      </button>
    </div>
  )
}
```

### Translation Files

```typescript
// lib/i18n.ts
export const translations = {
  en: {
    welcome: 'Welcome to consulting.sa',
    services: 'Our Services',
    // ... other translations
  },
  ar: {
    welcome: 'مرحباً بكم في المستشار.السعودية',
    services: 'خدماتنا',
    // ... other translations
  },
}
```

## 🔧 Configuration

### Environment Variables

The frontend uses environment variables from the project root `.env` file:

```env
# Core Application
NODE_ENV=development
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_ADMIN_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Contact
NEXT_PUBLIC_CONTACT_EMAIL=asim@consulting.sa

# Analytics (optional)
NEXT_PUBLIC_GA_ID=your_google_analytics_id

# Features
ANALYZE=false
NEXT_TELEMETRY_DISABLED=1
```

### Next.js Configuration

```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  images: {
    formats: ['image/webp', 'image/avif'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-supabase-project.supabase.co',
      },
    ],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

## 📱 Responsive Design

### Breakpoints

| Breakpoint | Size | Usage |
|------------|------|-------|
| `sm` | 640px+ | Small tablets |
| `md` | 768px+ | Tablets |
| `lg` | 1024px+ | Small desktops |
| `xl` | 1280px+ | Large desktops |
| `2xl` | 1536px+ | Extra large screens |

### Mobile-First Approach

```tsx
// Responsive component example
export function ResponsiveCard() {
  return (
    <div className="
      w-full 
      sm:w-1/2 
      lg:w-1/3 
      xl:w-1/4
      p-4 
      sm:p-6 
      lg:p-8
    ">
      <h2 className="text-lg sm:text-xl lg:text-2xl">
        Responsive Title
      </h2>
    </div>
  )
}
```

## 🚀 Performance Optimizations

### Image Optimization

```tsx
import Image from 'next/image'

// Optimized image component
export function OptimizedImage() {
  return (
    <Image
      src="/logo.webp"
      alt="consulting.sa logo"
      width={200}
      height={100}
      priority
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  )
}
```

### Code Splitting

```tsx
import dynamic from 'next/dynamic'

// Dynamic import for heavy components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false,
})
```

### Bundle Analysis

```bash
# Analyze bundle size
ANALYZE=true npm run build
```

## 🧪 Testing

### Test Structure

```
tests/
├── __tests__/              # Test files
│   ├── components/         # Component tests
│   ├── pages/              # Page tests
│   └── utils/              # Utility tests
├── __mocks__/              # Mock files
├── fixtures/               # Test fixtures
└── setup.ts               # Test setup
```

### Running Tests

```bash
# Run tests (when implemented)
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 🔍 API Routes

### Health Check Endpoints

```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'frontend',
  })
}
```

### Available Endpoints

- **GET /api/health** - Frontend health check
- **GET /api/health/database** - Database connectivity check
- **GET /api/metrics** - Application metrics
- **POST /api/chat** - Chat API endpoint
- **GET /api/admin/stats** - Admin statistics
- **GET /api/customer/dashboard** - Customer dashboard data

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

#### TypeScript Errors
```bash
# Run type checking
npm run type-check

# Check TypeScript configuration
npx tsc --showConfig
```

#### Styling Issues
```bash
# Rebuild Tailwind CSS
npm run build

# Check Tailwind configuration
npx tailwindcss --help
```

#### Runtime Errors
```bash
# Check browser console for errors
# Verify environment variables are set
# Check component imports and exports
```

### Error Solutions

#### "Module not found" errors
- Check import paths are correct
- Verify the file exists
- Check TypeScript path mapping in `tsconfig.json`

#### Hydration errors
- Ensure server and client render the same content
- Check for browser-only code in server components
- Use `useEffect` for client-only operations

#### Supabase connection errors
- Verify Supabase URL and keys in environment variables
- Check Supabase project status
- Review network connectivity

## 📊 Performance Monitoring

### Core Web Vitals

The application is optimized for:

- **LCP (Largest Contentful Paint)** < 2.5s
- **FID (First Input Delay)** < 100ms
- **CLS (Cumulative Layout Shift)** < 0.1

### Monitoring Tools

```tsx
// Performance monitoring component
import { PerformanceMonitor } from '@/components/performance-monitor'

export default function Layout({ children }) {
  return (
    <>
      <PerformanceMonitor />
      {children}
    </>
  )
}
```

## 🚀 Deployment

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Environment-Specific Builds

```bash
# Development build
NODE_ENV=development npm run build

# Production build
NODE_ENV=production npm run build
```

### Static Export (if needed)

```bash
# Configure in next.config.mjs
output: 'export'

# Build static export
npm run build
```

## 🔗 Related Documentation

- **[Local Testing Guide](../LOCAL_TESTING_GUIDE.md)** - Complete local testing setup
- **[Main README](../README.md)** - Project overview and setup
- **[Backend README](../backend/README.md)** - Backend documentation
- **[Infrastructure README](../infrastructure/README.md)** - Deployment documentation

## 📞 Support

For frontend-specific issues:

1. **Check browser console**: Look for JavaScript errors
2. **Verify environment**: Ensure all required variables are set
3. **Test build**: Run `npm run build` to check for build errors
4. **Review dependencies**: Run `npm install` to ensure all packages are installed

---

**Framework**: Next.js 15.4.1  
**Package Manager**: npm  
**Status**: Production Ready  
**Last Updated**: January 27, 2025