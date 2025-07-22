# Deployment Guide

This guide covers various deployment options for the Main Consulting website.

## 🚀 Quick Deploy Options

### Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/main-consulting/website)

1. **Connect Repository**
   - Import your GitHub repository to Vercel
   - Vercel will automatically detect Next.js configuration

2. **Configure Environment Variables**
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
   NEXT_PUBLIC_CONTACT_EMAIL=asim@main.consulting.sa
   ```

3. **Deploy**
   - Vercel will automatically build and deploy
   - Subsequent pushes to main branch trigger automatic deployments

### Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/main-consulting/website)

1. **Build Settings**
   - Build command: `npm run build`
   - Publish directory: `.next`

2. **Environment Variables**
   - Add the same environment variables as Vercel

## 🐳 Docker Deployment

### Local Docker

1. **Build Image**
   ```bash
   docker build -t main-consulting-website .
   ```

2. **Run Container**
   ```bash
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_SUPABASE_URL=your_url \
     -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key \
     main-consulting-website
   ```

### Docker Compose

1. **Create docker-compose.override.yml**
   ```yaml
   version: '3.8'
   services:
     web:
       environment:
         - NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
         - NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

### Production Docker

1. **Multi-stage Build**
   ```dockerfile
   # Build stage
   FROM node:18-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY . .
   RUN npm run build

   # Production stage
   FROM node:18-alpine AS runner
   WORKDIR /app
   ENV NODE_ENV production
   RUN addgroup --system --gid 1001 nodejs
   RUN adduser --system --uid 1001 nextjs
   COPY --from=builder /app/public ./public
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
   USER nextjs
   EXPOSE 3000
   ENV PORT 3000
   CMD ["node", "server.js"]
   ```

## ☁️ Cloud Platforms

### AWS

#### AWS Amplify
1. **Connect Repository**
   - Go to AWS Amplify Console
   - Connect your GitHub repository

2. **Build Settings**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

#### AWS ECS with Fargate
1. **Create Task Definition**
2. **Configure Service**
3. **Set up Load Balancer**
4. **Configure Auto Scaling**

### Google Cloud Platform

#### Cloud Run
1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/main-consulting
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT_ID/main-consulting --platform managed
   ```

### Microsoft Azure

#### Azure Container Instances
1. **Create Resource Group**
2. **Deploy Container**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name main-consulting \
     --image your-registry/main-consulting:latest \
     --ports 3000
   ```

## 🔧 Environment Configuration

### Production Environment Variables

```env
# Required
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Optional
NEXT_PUBLIC_CONTACT_EMAIL=asim@main.consulting.sa
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Security (Production)
NODE_ENV=production
```

### Development Environment Variables

```env
# Development
NODE_ENV=development
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_local_key

# Debug
DEBUG=true
ANALYZE=true
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use platform-specific secret management
- Rotate keys regularly

### Headers
The application includes security headers:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: origin-when-cross-origin

### HTTPS
- Always use HTTPS in production
- Configure SSL certificates
- Enable HSTS headers

## 📊 Performance Optimization

### Build Optimization
```bash
# Analyze bundle size
npm run analyze

# Type check before build
npm run type-check

# Clean build
npm run clean && npm run build
```

### CDN Configuration
- Configure CDN for static assets
- Enable compression (gzip/brotli)
- Set appropriate cache headers

## 🔍 Monitoring

### Health Checks
The application includes a health check endpoint:
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T10:00:00.000Z",
  "service": "main-consulting-website"
}
```

### Logging
- Configure structured logging
- Set up error tracking (Sentry)
- Monitor performance metrics

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clear cache
   npm run clean
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Environment Variables Not Loading**
   - Check file naming (`.env.local` for Next.js)
   - Verify variable names start with `NEXT_PUBLIC_`
   - Restart development server

3. **Docker Issues**
   ```bash
   # Check logs
   docker logs container_name
   
   # Debug container
   docker exec -it container_name sh
   ```

### Performance Issues
- Use `npm run analyze` to identify large bundles
- Check image optimization settings
- Verify CDN configuration

## 📞 Support

For deployment support:
- Email: asim@main.consulting.sa
- Documentation: [docs/](./docs/)
- Issues: GitHub Issues

---

**Last Updated**: January 2025