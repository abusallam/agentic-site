# 🔒 SSL Certificate Troubleshooting for Coolify + Traefik

## 🚨 Current Issue
**Error**: "Invalid SSL certificate" for `site.consulting.sa`
**Cause**: SSL certificate doesn't match the domain or wildcard configuration issue

## 🔍 Diagnosis Steps

### 1. Check Coolify Domain Configuration
In your Coolify dashboard:
- Go to your application settings
- Check the **Domains** tab
- Ensure domains are configured as:
  - `site.consulting.sa`
  - `admin.consulting.sa`

### 2. Verify Wildcard SSL Certificate
Check if your wildcard certificate covers `*.consulting.sa`:

```bash
# Check certificate details
openssl s_client -connect site.consulting.sa:443 -servername site.consulting.sa

# Look for Subject Alternative Names (SAN)
# Should include: *.consulting.sa or site.consulting.sa
```

### 3. Traefik Configuration Check
Verify Traefik is properly configured for wildcard SSL:

```bash
# Check Traefik logs
docker logs traefik-container-name

# Look for SSL certificate resolution errors
```

## 🛠️ Solutions

### Solution 1: Configure Domains in Coolify Dashboard

1. **Go to Application Settings**
2. **Navigate to Domains tab**
3. **Add domains individually**:
   - Add: `site.consulting.sa`
   - Add: `admin.consulting.sa`
4. **Enable SSL for each domain**
5. **Save and redeploy**

### Solution 2: Update Wildcard Certificate

If using Let's Encrypt wildcard:

```bash
# Generate wildcard certificate for *.consulting.sa
certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d "*.consulting.sa" \
  -d "consulting.sa"
```

### Solution 3: Manual Traefik Labels (if needed)

If Coolify doesn't handle it automatically, add these labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend.rule=Host(\`site.consulting.sa\`) || Host(\`admin.consulting.sa\`)"
  - "traefik.http.routers.frontend.tls=true"
  - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
  - "traefik.http.services.frontend.loadbalancer.server.port=3000"
```

### Solution 4: Use Single Domain with Path Routing

Alternative approach - use one domain with paths:

**Domain**: `consulting.sa`
**Routes**:
- `/` → Main site
- `/admin` → Admin panel

## 🔧 Coolify-Specific Fixes

### Option A: Let Coolify Manage Everything
Remove manual Traefik labels and let Coolify handle SSL:

```yaml
# In Coolify dashboard, set:
# Domain 1: site.consulting.sa
# Domain 2: admin.consulting.sa
# SSL: Enabled (Let's Encrypt)
```

### Option B: Manual Certificate Upload
If you have a valid wildcard certificate:

1. **Go to Coolify Settings**
2. **Navigate to SSL Certificates**
3. **Upload your wildcard certificate**
4. **Assign to your application**

## 🧪 Testing Steps

### 1. Test SSL Certificate
```bash
# Test site.consulting.sa
curl -I https://site.consulting.sa

# Test admin.consulting.sa  
curl -I https://admin.consulting.sa

# Check certificate validity
openssl s_client -connect site.consulting.sa:443 -servername site.consulting.sa < /dev/null
```

### 2. Test Application Routes
```bash
# Test main site
curl https://site.consulting.sa/api/health

# Test admin access
curl https://admin.consulting.sa/admin/dashboard
```

## 🚀 Recommended Solution

**For immediate fix**:

1. **In Coolify Dashboard**:
   - Go to your application
   - Domains tab
   - Remove existing domains
   - Add: `site.consulting.sa` (Enable SSL)
   - Add: `admin.consulting.sa` (Enable SSL)
   - Save and redeploy

2. **Wait for SSL provisioning** (2-5 minutes)

3. **Test both domains**:
   - https://site.consulting.sa
   - https://admin.consulting.sa

## 📞 If Issues Persist

### Check Coolify Logs
```bash
# Application logs
docker logs coolify-app-container

# Traefik logs  
docker logs coolify-traefik

# Certificate resolver logs
docker logs coolify-certresolver
```

### DNS Verification
```bash
# Verify DNS resolution
nslookup site.consulting.sa
nslookup admin.consulting.sa

# Check A records point to correct IP
dig site.consulting.sa A
dig admin.consulting.sa A
```

### Contact Points
- **Coolify Documentation**: Check SSL configuration guide
- **Traefik Docs**: SSL certificate troubleshooting
- **Let's Encrypt**: Certificate validation issues

---

## 🎯 Expected Result

After fixing:
- ✅ https://site.consulting.sa → Main website
- ✅ https://admin.consulting.sa → Admin dashboard  
- ✅ Valid SSL certificates for both domains
- ✅ Automatic HTTPS redirect
- ✅ No certificate warnings

The SSL issue should be resolved with proper domain configuration in Coolify! 🔒