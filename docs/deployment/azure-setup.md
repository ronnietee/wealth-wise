# Azure App Service Quick Setup Guide

## Prerequisites
1. Azure account (https://azure.microsoft.com/free/)
2. Azure CLI installed (optional but helpful)

## Quick Setup via Azure Portal

### 1. Create App Service
1. Go to https://portal.azure.com
2. "Create a resource" → "Web App"
3. Fill in:
   - **Name**: `steward-app` (must be unique)
   - **Runtime**: Python 3.11
   - **Plan**: Free F1
4. Create

### 2. Create PostgreSQL Database
1. "Create a resource" → "Azure Database for PostgreSQL"
2. Choose "Flexible Server"
3. Configure:
   - **Server name**: `steward-db`
   - **Compute**: Burstable B1ms (free tier eligible)
   - Set admin credentials
4. In "Networking", allow Azure services

### 3. Configure App Settings
In your App Service → Configuration → Application settings:

**Required:**
```
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@steward-db.postgres.database.azure.com/postgres?sslmode=require
SECRET_KEY=<generate-strong-secret>
JWT_SECRET_KEY=<generate-strong-secret>
```

**Startup Command:**
In Configuration → General settings:
```
gunicorn --bind 0.0.0.0:8000 app:app
```

### 4. Deploy from GitHub
1. App Service → Deployment Center
2. Connect GitHub
3. Select repository
4. Auto-deploys on push

## Using Azure CLI (Alternative)

If you prefer command line, use the provided `azure-deploy.sh` script:

```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

Or manually:
```bash
# Login
az login

# Create resource group
az group create --name steward-rg --location eastus

# Create App Service Plan (Free)
az appservice plan create --name steward-plan --resource-group steward-rg --sku FREE --is-linux

# Create Web App
az webapp create --name steward-app --resource-group steward-rg --plan steward-plan --runtime "PYTHON:3.11"

# Set startup command
az webapp config set --name steward-app --resource-group steward-rg --startup-file "gunicorn --bind 0.0.0.0:8000 app:app"

# Set environment variables
az webapp config appsettings set --name steward-app --resource-group steward-rg --settings FLASK_ENV=production DATABASE_URL="..."
```

## Important Notes

### Free Tier Limitations
- ⚠️ App sleeps after 20 minutes of inactivity
- ⚠️ Takes ~30 seconds to wake up
- ⚠️ 60 minutes compute per day
- ⚠️ Shared infrastructure (slower)

### For Production
Upgrade to **Basic B1** plan (~$13/month) for:
- Always-on (no sleep)
- Better performance
- More resources

### Database Connection
- Use **Internal connection string** from PostgreSQL
- Format: `postgresql://user:pass@server.postgres.database.azure.com/db?sslmode=require`
- Enable "Allow Azure services" in firewall rules

### Environment Variables
Set all variables in App Service → Configuration → Application settings (not in .env file)

### Custom Domain
1. App Service → Custom domains
2. Add your domain
3. Follow DNS configuration instructions
4. SSL certificate is automatic (free)

## Troubleshooting

### App won't start
- Check logs: App Service → Log stream
- Verify startup command is set
- Check environment variables

### Database connection fails
- Verify firewall rules allow Azure services
- Check connection string format
- Ensure SSL is enabled (`sslmode=require`)

### Slow performance
- Free tier uses shared infrastructure
- Consider upgrading to Basic plan
- Check application logs for bottlenecks

