# Troubleshooting Guide - Coolify 404 Error

This guide helps resolve the 404 "Page Not Found" error when deploying to Coolify.

## 🔍 Common Causes of 404 Error

### 1. **Port Configuration Issue**
- **Problem**: Coolify not routing traffic to the correct port
- **Solution**: Ensure port 3000 is properly exposed and configured

### 2. **Container Not Starting Properly**
- **Problem**: Application fails to start but container appears running
- **Solution**: Check application logs in Coolify dashboard

### 3. **Build Output Issues**
- **Problem**: Next.js build doesn't generate proper files
- **Solution**: Verify build process and standalone output

### 4. **Environment Variables Missing**
- **Problem**: Required environment variables not set
- **Solution**: Configure all necessary environment variables

## 🛠️ Troubleshooting Steps

### Step 1: Check Coolify Logs
1. Go to Coolify Dashboard
2. Select your application
3. Click on "Logs" tab
4. Look for error messages during startup

### Step 2: Verify Container Health
1. Check if container is running: `docker ps`
2. Test health endpoint: `curl http://localhost:3000/api/health`
3. Check container logs: `docker logs <container_id>`

### Step 3: Test Local Build
```bash
# Test the build locally
npm run build
npm start

# Test with Docker
docker build -t test-app .
docker run -p 3000:3000 test-app
```

### Step 4: Verify Environment Variables
Ensure these are set in Coolify:
```env
NODE_ENV=production
PORT=3000
HOSTNAME=0.0.0.0
NEXT_TELEMETRY_DISABLED=1
```

## 🔧 Solutions

### Solution 1: Use Simple Dockerfile
If the multi-stage build is causing issues, use `Dockerfile.simple`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
ENV NODE_ENV=production
ENV PORT=3000
CMD ["npm", "start"]
```

### Solution 2: Update Coolify Configuration
1. **Port Settings**: Ensure port is set to 3000
2. **Health Check**: Set to `/api/health`
3. **Domain**: Verify domain points to correct IP
4. **SSL**: Ensure SSL certificate is valid

### Solution 3: Simplified Next.js Config
Use the cleaned up configuration without complex plugins:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  compress: true,
  // ... rest of config
}

export default nextConfig
```

### Solution 4: Check DNS and Domain
1. Verify DNS records point to Coolify server
2. Check if domain is properly configured in Coolify
3. Ensure SSL certificate is active

## 🚨 Emergency Fixes

### Quick Fix 1: Use Standard Dockerfile
Replace current Dockerfile with `Dockerfile.simple` and redeploy.

### Quick Fix 2: Disable Standalone Mode
Temporarily remove `output: 'standalone'` from next.config.mjs.

### Quick Fix 3: Check Port Binding
Ensure Coolify is configured to route traffic to port 3000.

## 📊 Debugging Commands

### Check Container Status
```bash
# List running containers
docker ps

# Check specific container logs
docker logs <container_name>

# Execute into container
docker exec -it <container_name> sh
```

### Test Application Locally
```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test main page
curl http://localhost:3000/

# Check if server is listening
netstat -tlnp | grep 3000
```

### Coolify Specific Checks
1. **Application Status**: Check if marked as "Running"
2. **Build Logs**: Review for any build failures
3. **Runtime Logs**: Check for startup errors
4. **Domain Configuration**: Verify domain settings
5. **SSL Status**: Ensure certificate is active

## 📞 Getting Help

### Log Information to Collect
1. **Build Logs**: From Coolify dashboard
2. **Runtime Logs**: Application startup logs
3. **Container Status**: `docker ps` output
4. **Health Check**: Response from `/api/health`
5. **Environment Variables**: List of configured variables

### Common Error Messages
- "ECONNREFUSED": Port not accessible
- "Cannot GET /": Routing issue
- "Module not found": Build dependency issue
- "Permission denied": File permission issue

---

**Last Updated**: January 18, 2025
**Status**: Ready for troubleshooting