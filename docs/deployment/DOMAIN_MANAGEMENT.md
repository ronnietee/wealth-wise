# Domain Management Guide

This guide covers how to manage domain changes when deploying, migrating, or updating your STEWARD application.

---

## Table of Contents

1. [How Domains Are Used in STEWARD](#how-domains-are-used)
2. [Setting Up Custom Domains](#setting-up-custom-domains)
3. [Changing Domains on Render](#changing-domains-on-render)
4. [Changing Domains on Azure](#changing-domains-on-azure)
5. [DNS Configuration](#dns-configuration)
6. [Environment Variables to Update](#environment-variables-to-update)
7. [Domain Migration Checklist](#domain-migration-checklist)
8. [Troubleshooting](#troubleshooting)

---

## How Domains Are Used in STEWARD

### Automatic Domain Detection (Good ✅)

Your app uses `request.url_root` in these places, which **automatically detects** the current domain:

**Files using auto-detection:**
- `src/utils/email.py` - Email verification links
- `src/utils/email.py` - Password reset links
- `src/services/email_service.py` - Subscription email links

**Example:**
```python
verification_url = f"{request.url_root}verify-email?token={verification_token}"
```

✅ **No changes needed** - These automatically use the correct domain!

### Manual Domain Configuration (Needs Updates ⚠️)

These require manual updates when domain changes:

1. **PayFast URLs** (in environment variables):
   - `PAYFAST_RETURN_URL`
   - `PAYFAST_CANCEL_URL`
   - `PAYFAST_NOTIFY_URL`

2. **Hardcoded localhost check** (in `templates/settings.html`):
   - Used for test mode detection

---

## Setting Up Custom Domains

### On Render

#### Step 1: Add Custom Domain
1. Go to your Render dashboard
2. Select your web service
3. Go to **Settings** → **Custom Domains**
4. Click **Add Custom Domain**
5. Enter your domain (e.g., `steward.com` or `www.steward.com`)

#### Step 2: Configure DNS
Render will show you DNS records to add:

**For root domain (steward.com):**
```
Type: A
Name: @
Value: <Render IP address>
```

**For www subdomain (www.steward.com):**
```
Type: CNAME
Name: www
Value: <your-app>.onrender.com
```

#### Step 3: SSL Certificate
- Render automatically provisions SSL certificates
- Takes 5-10 minutes after DNS propagates
- Certificate is free and auto-renewed

#### Step 4: Update Environment Variables
After domain is active, update PayFast URLs:
```
PAYFAST_RETURN_URL=https://steward.com/payfast/return
PAYFAST_CANCEL_URL=https://steward.com/payfast/cancel
PAYFAST_NOTIFY_URL=https://steward.com/api/subscriptions/webhook/payfast
```

---

### On Azure

#### Step 1: Add Custom Domain
1. Go to Azure Portal → Your App Service
2. Go to **Custom domains**
3. Click **Add custom domain**
4. Enter your domain name
5. Click **Validate**

#### Step 2: Configure DNS
Azure will show you DNS records to add:

**For root domain:**
```
Type: A
Name: @
Value: <Azure IP address>
```

**For www subdomain:**
```
Type: CNAME
Name: www
Value: <your-app>.azurewebsites.net
```

#### Step 3: SSL Certificate
1. After DNS propagates, go to **TLS/SSL settings**
2. Click **Add TLS/SSL binding**
3. Select your domain
4. Choose **SNI SSL** (free) or **IP SSL** (paid)
5. Click **Add**

#### Step 4: Update Environment Variables
Update PayFast URLs in App Service → Configuration:
```
PAYFAST_RETURN_URL=https://steward.com/payfast/return
PAYFAST_CANCEL_URL=https://steward.com/payfast/cancel
PAYFAST_NOTIFY_URL=https://steward.com/api/subscriptions/webhook/payfast
```

---

## Changing Domains on Render

### Scenario 1: Change from Default (.onrender.com) to Custom Domain

1. **Add custom domain** (see above)
2. **Wait for DNS propagation** (24-48 hours, usually faster)
3. **Update environment variables** with new domain
4. **Test all features** (email links, PayFast, etc.)
5. **Optional**: Set up redirect from old domain to new

### Scenario 2: Change Custom Domain

1. **Remove old domain** from Render dashboard
2. **Add new domain** and configure DNS
3. **Update environment variables**
4. **Update DNS records** at your registrar
5. **Wait for propagation** and test

### Scenario 3: Migrate from Render to Azure (Domain Change)

1. **Set up Azure** with new domain
2. **Configure DNS** to point to Azure
3. **Update environment variables** on Azure
4. **Test thoroughly** on Azure
5. **Update DNS** (change A/CNAME records)
6. **Keep Render running** for 48h as backup
7. **Monitor** both environments
8. **Shut down Render** after verification

---

## Changing Domains on Azure

### Update Domain in Azure Portal

1. Go to **Custom domains**
2. Click **Add custom domain**
3. Enter new domain
4. Follow DNS configuration steps
5. Update SSL certificate binding

### Update Environment Variables

1. Go to **Configuration** → **Application settings**
2. Update PayFast URLs:
   ```
   PAYFAST_RETURN_URL=https://new-domain.com/payfast/return
   PAYFAST_CANCEL_URL=https://new-domain.com/payfast/cancel
   PAYFAST_NOTIFY_URL=https://new-domain.com/api/subscriptions/webhook/payfast
   ```
3. Click **Save**
4. App will restart automatically

---

## DNS Configuration

### Common DNS Record Types

#### A Record (IPv4 Address)
```
Type: A
Name: @ (or blank for root domain)
Value: <IP address>
TTL: 3600 (or default)
```

#### CNAME Record (Alias)
```
Type: CNAME
Name: www
Value: your-app.onrender.com (or your-app.azurewebsites.net)
TTL: 3600
```

#### TXT Record (Verification)
```
Type: TXT
Name: @
Value: <verification string from platform>
TTL: 3600
```

### DNS Propagation

- **Typical time**: 1-48 hours
- **Usually faster**: 15 minutes to 2 hours
- **Check propagation**: Use https://dnschecker.org
- **Reduce TTL**: Set to 300 (5 min) before migration for faster updates

### Pre-Migration DNS Setup

**24 hours before migration:**
1. Reduce DNS TTL to 300 seconds (5 minutes)
2. This allows faster DNS updates during migration

**During migration:**
1. Update DNS records to point to new platform
2. Monitor DNS propagation
3. Test both old and new domains

---

## Environment Variables to Update

### When Domain Changes, Update These:

#### Required Updates

```bash
# PayFast URLs (if using PayFast)
PAYFAST_RETURN_URL=https://your-new-domain.com/payfast/return
PAYFAST_CANCEL_URL=https://your-new-domain.com/payfast/cancel
PAYFAST_NOTIFY_URL=https://your-new-domain.com/api/subscriptions/webhook/payfast
```

#### Optional Updates (for reference)

```bash
# These are auto-detected, but you can set explicitly if needed
# (Not required - request.url_root handles this automatically)
```

### Where to Update

#### Render
1. Dashboard → Your Service → **Environment**
2. Edit variables
3. Click **Save Changes**
4. Service restarts automatically

#### Azure
1. Portal → App Service → **Configuration** → **Application settings**
2. Edit variables
3. Click **Save**
4. App restarts automatically

---

## Domain Migration Checklist

### Pre-Migration (1 week before)

- [ ] Document current domain configuration
- [ ] List all environment variables with domains
- [ ] Reduce DNS TTL to 300 seconds
- [ ] Set up new platform (Render/Azure)
- [ ] Test new platform with temporary domain
- [ ] Prepare rollback plan

### Migration Day

- [ ] Set up custom domain on new platform
- [ ] Configure DNS records
- [ ] Update environment variables
- [ ] Wait for DNS propagation (check with dnschecker.org)
- [ ] Test SSL certificate activation
- [ ] Verify email links work
- [ ] Test PayFast integration (if used)
- [ ] Test all user flows
- [ ] Monitor error logs

### Post-Migration (48 hours)

- [ ] Monitor both old and new domains
- [ ] Check error rates
- [ ] Verify all features work
- [ ] Test email delivery
- [ ] Check PayFast webhooks (if used)
- [ ] Update documentation
- [ ] Shut down old platform (after 48h verification)

---

## Troubleshooting

### Domain Not Resolving

**Symptoms**: Domain shows "not found" or times out

**Solutions**:
1. Check DNS records are correct
2. Wait for DNS propagation (can take up to 48h)
3. Verify DNS at https://dnschecker.org
4. Check domain registrar settings
5. Verify platform domain configuration

### SSL Certificate Not Working

**Symptoms**: "Not Secure" warning, SSL errors

**Solutions**:
1. Wait 10-15 minutes after DNS propagation
2. Check SSL certificate status in platform dashboard
3. Verify DNS records are correct
4. Clear browser cache
5. Try incognito/private browsing mode
6. Check certificate expiration date

### Email Links Use Wrong Domain

**Symptoms**: Email verification/reset links point to old domain

**Solutions**:
1. Check that `request.url_root` is working correctly
2. Verify environment variables
3. Check Flask app configuration
4. Clear application cache
5. Restart application

### PayFast Webhooks Not Working

**Symptoms**: Payment notifications not received

**Solutions**:
1. Verify `PAYFAST_NOTIFY_URL` is updated
2. Check PayFast merchant dashboard for webhook logs
3. Ensure domain is accessible (not blocked)
4. Check SSL certificate is valid
5. Verify webhook endpoint is accessible

### Mixed Content Warnings

**Symptoms**: Browser shows mixed HTTP/HTTPS warnings

**Solutions**:
1. Ensure all URLs use HTTPS
2. Check environment variables use `https://`
3. Update any hardcoded HTTP URLs
4. Verify platform forces HTTPS
5. Check browser console for specific resources

---

## Best Practices

### 1. Use Environment Variables
✅ Store domain-dependent URLs in environment variables
❌ Don't hardcode domains in code

### 2. Use Auto-Detection When Possible
✅ Use `request.url_root` for dynamic URLs
❌ Don't hardcode domain in email templates

### 3. Test Before Migration
✅ Test new domain thoroughly before switching DNS
❌ Don't switch DNS without testing

### 4. Keep Backup
✅ Keep old platform running for 48h after migration
❌ Don't shut down old platform immediately

### 5. Monitor Closely
✅ Monitor error logs and user feedback
❌ Don't assume everything works automatically

### 6. Document Changes
✅ Document all domain changes and DNS records
❌ Don't rely on memory for configuration

---

## Quick Reference: Domain Update Commands

### Render (via Dashboard)
1. Settings → Custom Domains → Add/Update
2. Environment → Update variables → Save

### Azure (via Portal)
1. Custom domains → Add custom domain
2. Configuration → Application settings → Update → Save

### Azure (via CLI)
```bash
# Update environment variable
az webapp config appsettings set \
  --name your-app \
  --resource-group your-rg \
  --settings PAYFAST_RETURN_URL="https://new-domain.com/payfast/return"
```

---

## Common Domain Scenarios

### Scenario 1: Adding www Subdomain
1. Add CNAME record: `www` → `your-app.onrender.com`
2. Configure in platform dashboard
3. SSL auto-provisions
4. Optional: Set up redirect from root to www (or vice versa)

### Scenario 2: Moving from Subdomain to Root Domain
1. Set up root domain (A record)
2. Update environment variables
3. Test thoroughly
4. Remove subdomain configuration

### Scenario 3: Platform Migration (Render → Azure)
1. Set up Azure with new domain
2. Configure DNS to point to Azure
3. Update environment variables
4. Test on Azure
5. Switch DNS
6. Monitor both platforms
7. Shut down Render after verification

---

## Need Help?

If you encounter issues:
1. Check platform-specific documentation
2. Review DNS propagation status
3. Check application logs
4. Verify environment variables
5. Test with curl/Postman for API endpoints

For platform-specific help:
- **Render**: https://render.com/docs
- **Azure**: https://docs.microsoft.com/azure/app-service

