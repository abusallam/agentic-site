# 🔒 SSL Configuration & Troubleshooting Guide

## Current Domain Configuration
- **Main Site**: https://site.consulting.sa
- **Admin Panel**: https://admin.consulting.sa

## SSL Issues & Solutions

### 1. **DNS Configuration Check**

Ensure your DNS records are properly configured:

```dns
# A Records (pointing to your Coolify server IP)
site.consulting.sa    A    YOUR_COOLIFY_SERVER_IP
admin.consulting.sa   A    YOUR_COOLIFY_SERVER_IP

# Optional CNAME (if using load balancer)
site.consulting.sa    CNAME    your-coolify-domain.com
admin.consulting.sa   CNAME    your-coolify-domain.com
```

### 2. **Coolify SSL Configuration**

Current configuration in `docker-compose.coolify.yml`:
```yaml
- "coolify.domains=site.consulting.sa,admin.consulting.sa"
- "coolify.ssl=true"
- "coolify.ssl.letsencrypt=true"
- "coolify.ssl.force=true"
- "coolify.redirect=true"
- "coolify.redirect.www=false"
```

### 3. **Common SSL Issues & Fixes**

#### Issue 1: Certificate Generation Failed
**Symptoms**: SSL certificate not generated, browser shows "Not Secure"

**Solutions**:
1. **Check DNS propagation**:
   ```bash
   nslookup site.consulting.sa
   nslookup admin.consulting.sa
   ```

2. **Verify domain accessibility**:
   ```bash
   curl -I http://site.consulting.sa
   curl -I http://admin.consulting.sa
   ```

3. **In Coolify Dashboard**:
   - Go to your application
   - Navigate to "Domains" tab
   - Click "Generate SSL Certificate"
   - Monitor logs for errors

#### Issue 2: Mixed Content Errors
**Symptoms**: Some resources load over HTTP instead of HTTPS

**Solutions**:
1. **Update environment variables**:
   ```env
   NEXT_PUBLIC_SITE_URL=https://site.consulting.sa
   NEXT_PUBLIC_API_URL=https://site.consulting.sa/api
   ```

2. **Force HTTPS in Next.js**:
   - Already configured in `next.config.mjs`
   - Security headers enforce HTTPS

#### Issue 3: Subdomain Certificate Issues
**Symptoms**: Certificate works for one domain but not the other

**Solutions**:
1. **Use separate applications** (Recommended):
   - Create separate Coolify applications for each subdomain
   - Deploy same codebase to both
   - Configure different environment variables

2. **Use wildcard certificate**:
   - Configure `*.consulting.sa` in DNS
   - Update Coolify to use wildcard domain

### 4. **Recommended Coolify Setup**

#### Option A: Single Application (Current)
```yaml
# Single app serving both domains
domains: "site.consulting.sa,admin.consulting.sa"
```

#### Option B: Separate Applications (Recommended)
```yaml
# App 1: Main Site
domains: "site.consulting.sa"
environment:
  - NEXT_PUBLIC_APP_TYPE=main

# App 2: Admin Panel  
domains: "admin.consulting.sa"
environment:
  - NEXT_PUBLIC_APP_TYPE=admin
```

### 5. **Environment Variables for SSL**

Add these to your Coolify environment:

```env
# SSL Configuration
NEXT_PUBLIC_SITE_URL=https://site.consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://admin.consulting.sa
NEXT_PUBLIC_API_URL=https://site.consulting.sa/api

# Force HTTPS
FORCE_HTTPS=true
NODE_TLS_REJECT_UNAUTHORIZED=0

# Security Headers
HSTS_MAX_AGE=31536000
```

### 6. **Debugging SSL Issues**

#### Check Certificate Status:
```bash
# Check SSL certificate
openssl s_client -connect site.consulting.sa:443 -servername site.consulting.sa
openssl s_client -connect admin.consulting.sa:443 -servername admin.consulting.sa

# Check certificate expiry
curl -vI https://site.consulting.sa 2>&1 | grep -i expire
```

#### Check Coolify Logs:
1. Go to Coolify Dashboard
2. Navigate to your application
3. Check "Logs" tab for SSL-related errors
4. Look for Let's Encrypt certificate generation logs

### 7. **Next.js SSL Configuration**

Update your `next.config.mjs` for better SSL handling:

```javascript
// Add to headers configuration
{
  source: '/(.*)',
  headers: [
    {
      key: 'Strict-Transport-Security',
      value: 'max-age=31536000; includeSubDomains; preload'
    },
    {
      key: 'Content-Security-Policy',
      value: "upgrade-insecure-requests"
    }
  ]
}
```

### 8. **Troubleshooting Steps**

1. **Verify DNS Resolution**:
   ```bash
   dig site.consulting.sa
   dig admin.consulting.sa
   ```

2. **Test HTTP Access**:
   ```bash
   curl -I http://site.consulting.sa
   curl -I http://admin.consulting.sa
   ```

3. **Check Coolify Configuration**:
   - Verify domain settings
   - Check SSL certificate status
   - Review deployment logs

4. **Test SSL Certificate**:
   ```bash
   curl -I https://site.consulting.sa
   curl -I https://admin.consulting.sa
   ```

### 9. **Alternative Solutions**

#### If Let's Encrypt Fails:
1. **Use Cloudflare SSL**:
   - Point domains to Cloudflare
   - Enable "Full (Strict)" SSL mode
   - Use Cloudflare's SSL certificates

2. **Manual Certificate**:
   - Generate SSL certificate manually
   - Upload to Coolify
   - Configure custom certificate

#### If Subdomains Don't Work:
1. **Use Path-Based Routing**:
   ```
   https://consulting.sa/site
   https://consulting.sa/admin
   ```

2. **Use Single Domain**:
   ```
   https://consulting.sa (main site)
   https://consulting.sa/admin (admin panel)
   ```

### 10. **Quick Fixes to Try**

1. **Redeploy Application**:
   - Force redeploy in Coolify
   - Wait for SSL certificate generation

2. **Clear DNS Cache**:
   ```bash
   # On your local machine
   sudo systemctl flush-dns  # Linux
   dscacheutil -flushcache   # macOS
   ```

3. **Check Firewall**:
   - Ensure ports 80 and 443 are open
   - Verify Coolify server accessibility

4. **Update Environment Variables**:
   - Add SSL-specific variables
   - Force HTTPS redirects

## Contact Support

If SSL issues persist:
1. Check Coolify documentation
2. Review server logs
3. Verify DNS configuration
4. Consider using Cloudflare as SSL proxy

---

**Current Status**: SSL configuration updated for your domains
**Next Step**: Deploy and monitor SSL certificate generation