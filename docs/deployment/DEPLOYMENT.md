# Deployment Guide for STEWARD

This guide covers deploying STEWARD to Render (primary platform) and alternative platforms.

## Branch Strategy

**Important**: Render deployments should use the `development` branch, not `master`:
- **`master`**: Stable, production-ready code
- **`development`**: Active development and testing branch (deployed to Render)

When setting up Render, connect it to the `development` branch for automatic deployments.

## Recommended Platform: Render

**Render is the recommended platform** for deploying STEWARD because:
- ✅ **Free tier available** (750 hours/month - enough for 24/7)
- ✅ **Free PostgreSQL database** included
- ✅ **Easy setup** with automatic SSL
- ✅ **Production ready** - suitable for commercial use
- ✅ **Automatic deployments** from GitHub
- ✅ **Simple configuration**

---

## Render Deployment (Primary)

### Prerequisites
1. GitHub account (push your code to GitHub)
2. Render account (sign up at https://render.com)

### Step-by-Step Deployment

#### 1. Push Code to GitHub
```bash
# If not already done, create a GitHub repo and push:
git remote add origin https://github.com/yourusername/wealth-wise.git
git push -u origin main
```

#### 2. Configure Render to Use Development Branch
1. In Render dashboard → Your Web Service → Settings
2. Under "Build & Deploy", set **Branch** to `development`
3. This ensures Render deploys from the development branch, keeping master stable

#### 3. Create PostgreSQL Database on Render
1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Name it: `steward-db`
4. Select "Free" plan
5. Click "Create Database"
6. **Copy the Internal Database URL** (you'll need this)

#### 4. Deploy Web Service
1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `steward-app`
   - **Environment**: `Python 3`
   - **Python Version**: `3.11.5` (set in Environment Variables or use runtime.txt)
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
   
   **Important**: If Render uses Python 3.13, you may need to:
   - Set `PYTHON_VERSION=3.11.5` in Environment Variables, OR
   - Update `psycopg2-binary` to latest version (already updated to 2.9.10)

#### 5. Set Environment Variables
In the Render dashboard, go to your web service → Environment tab, add:

**Required Variables:**
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here (generate a strong random string)
JWT_SECRET_KEY=your-jwt-secret-key-here (generate a strong random string)
DATABASE_URL=<from PostgreSQL service - Internal Database URL>
```

**Email Configuration:**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
CONTACT_EMAIL=your-email@gmail.com
```

**Optional (if using PayFast):**
```
PAYFAST_MERCHANT_ID=your-merchant-id
PAYFAST_MERCHANT_KEY=your-merchant-key
PAYFAST_PASSPHRASE=your-passphrase
PAYFAST_TEST_MODE=true
PAYFAST_RETURN_URL=https://your-app.onrender.com/payfast/return
PAYFAST_CANCEL_URL=https://your-app.onrender.com/payfast/cancel
PAYFAST_NOTIFY_URL=https://your-app.onrender.com/api/subscriptions/webhook/payfast
```

**Admin Configuration:**
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<generate using: python generate_admin_password.py>
```

#### 5. Deploy
Click "Create Web Service" and Render will:
- Clone your repo
- Install dependencies
- Run database migrations
- Start your app

#### 6. Access Your App
Your app will be available at: `https://steward-app.onrender.com`

---

## Alternative: Railway (Free Tier with $5 Credit)

### Setup Steps
1. Sign up at https://railway.app
2. Create new project → "Deploy from GitHub repo"
3. Add PostgreSQL database
4. Set environment variables (same as Render)
5. Railway auto-detects Python and deploys

**Note**: Railway gives $5 free credit monthly, then charges per usage.

---

## Alternative: Fly.io (Free Tier)

### Setup Steps
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `fly auth signup`
3. Create app: `fly launch`
4. Add PostgreSQL: `fly postgres create`
5. Set secrets: `fly secrets set SECRET_KEY=... DATABASE_URL=...`
6. Deploy: `fly deploy`

---

## Important Notes

### Database Migration
- On first deploy, migrations run automatically via `flask db upgrade` in build command
- If you encounter "Multiple head revisions" error, ensure the merge migration (`merge_heads_001`) is included
- If you need to run migrations manually later, use Render's shell or SSH
- **If you get column errors after deployment**, manually run migrations:
  1. Go to Render dashboard → Your service → Shell
  2. Run: `flask db upgrade`
  3. This will apply any pending migrations

### Environment Variables
- **Never commit** `.env` file to GitHub
- Use Render's environment variables UI
- Generate strong secrets for `SECRET_KEY` and `JWT_SECRET_KEY`

### Static Files
- Static files are served automatically by Flask
- No additional configuration needed

### Email Setup
- For Gmail, use an App Password (not your regular password)
- Enable 2FA on Gmail first
- Generate App Password: Google Account → Security → App Passwords

### Admin Access
- Generate admin password hash: `python generate_admin_password.py`
- Use the hash in `ADMIN_PASSWORD_HASH` environment variable

### SSL/HTTPS
- Render provides free SSL certificates automatically
- Your app will be HTTPS by default

### Custom Domain (Optional)
- In Render dashboard → Settings → Custom Domain
- Add your domain and follow DNS setup instructions

---

## Troubleshooting

### App Won't Start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt

### Database Connection Issues
- Use Internal Database URL (not External)
- Verify DATABASE_URL is set correctly
- Check database is running in Render dashboard

### Email Not Working
- Verify SMTP credentials
- Check firewall/security settings
- Test with debug logging enabled

### 404 Errors
- Check that all routes are registered
- Verify static files path is correct
- Check Flask app structure

---

## Post-Deployment Checklist

- [ ] App is accessible via HTTPS
- [ ] Database migrations completed
- [ ] Can register new user
- [ ] Can login
- [ ] Email sending works (test contact form)
- [ ] Admin panel accessible
- [ ] Static files loading (CSS, images)
- [ ] API endpoints working

---

## Cost Comparison

| Platform | Free Tier | Database | Production Ready | Notes |
|----------|-----------|----------|------------------|-------|
| **Azure** | F1 (60 min/day) | PostgreSQL available | ✅ Yes | Best for production, commercial use allowed |
| **Render** | 750 hrs/month | Free PostgreSQL | ✅ Yes | Easiest setup, good for testing |
| **Railway** | $5 credit/month | Included | ✅ Yes | Pay-as-you-go after credit |
| **Fly.io** | 3 shared VMs | Separate pricing | ✅ Yes | Good for containers |
| **Vercel** | Hobby plan | ❌ Not suitable | ❌ No | Non-commercial only, serverless only |

## Production Recommendations

### For Production Use:
1. **Azure App Service** (F1 free tier or Basic B1 for $13/month)
   - Best for commercial/production use
   - Enterprise infrastructure
   - Easy scaling path

2. **Render** (Free tier or Starter $7/month)
   - Easiest deployment
   - Good for small to medium apps
   - Simple scaling

### For Testing Only:
- **Render Free Tier**: 750 hours/month (enough for 24/7 testing)
- **Railway**: $5 free credit monthly

### Not Recommended:
- **Vercel**: Not suitable for Flask apps (serverless architecture mismatch)

---

## Migration Strategy: Render → Azure

**Recommended Approach**: Start on Render, migrate to Azure when you scale.

### When to Consider Migration:
- **500-1,000+ active users**
- **Performance issues** (slow queries, timeouts)
- **Need enterprise features** (staging slots, advanced monitoring)
- **Cost >$25/month** on Render (Azure becomes competitive)
- **Compliance requirements** (SOC 2, HIPAA, etc.)

### Migration Benefits:
- ✅ Better scalability (auto-scaling)
- ✅ Enterprise infrastructure
- ✅ Global regions for better performance
- ✅ Advanced security features

**See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed migration steps and timeline.**

**See [azure-setup.md](./azure-setup.md) for Azure deployment instructions when ready to migrate.**

