# Subscription Renewal Cron Job Setup

This guide explains how to set up automated subscription renewal processing.

## Overview

The renewal process checks all active subscriptions and extends their billing periods when due. This should run **daily** to ensure subscriptions are renewed on time.

## Prerequisites

1. Admin credentials configured in `.env`:
   ```bash
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```

2. Application URL configured (optional, defaults to `http://localhost:5000`):
   ```bash
   APP_URL=http://your-domain.com
   ```

3. Python 3 with `requests` library:
   ```bash
   pip install requests
   ```

## Setup Methods

### Method 1: Linux/Unix (cron) - Recommended for Production

#### Step 1: Create Logs Directory
```bash
mkdir -p logs
```

#### Step 2: Make Script Executable
```bash
chmod +x scripts/renewals.sh
```

#### Step 3: Test Manually
```bash
./scripts/renewals.sh
```

You should see output indicating successful renewal processing.

#### Step 4: Add to Crontab

Edit your crontab:
```bash
crontab -e
```

Add the following line (adjust path as needed):
```bash
# Process subscription renewals daily at 2:00 AM
0 2 * * * /full/path/to/wealth-wise/scripts/renewals.sh >> /full/path/to/wealth-wise/logs/renewals.log 2>&1
```

**Note**: Use absolute paths in crontab entries.

#### Step 5: Verify Installation
```bash
# View your crontab entries
crontab -l

# Check logs after the first run
tail -f logs/renewals.log
```

### Method 2: Windows Task Scheduler

#### Step 1: Create Batch File

Create `scripts/renewals.bat`:

```batch
@echo off
cd /d "%~dp0\.."
for /f "delims=" %%x in (.env) do set "%%x"
set APP_URL=http://localhost:5000
python scripts\process_renewals.py >> logs\renewals.log 2>&1
```

#### Step 2: Create Task in Task Scheduler

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. **Name**: "Process Subscription Renewals"
4. **Description**: "Daily renewal processing for STEWARD subscriptions"
5. **Trigger**: Daily at 2:00 AM
6. **Action**: Start a program
   - **Program/script**: `python` (or full path: `C:\Python39\python.exe`)
   - **Add arguments**: `scripts\process_renewals.py`
   - **Start in**: `C:\path\to\wealth-wise`
7. **Conditions**: 
   - Check "Start the task only if the computer is on AC power" (uncheck if not applicable)
   - Uncheck "Start the task only if the following network connection is available"
8. **Settings**:
   - Check "Run task as soon as possible after a scheduled start is missed"
   - "If the task is already running": Do not start a new instance
9. Click **Finish**

#### Step 3: Configure Environment Variables

Since `.env` files don't load automatically in Windows Task Scheduler, you have two options:

**Option A**: Set environment variables in Task Scheduler:
1. Right-click your task → **Properties**
2. **General** tab → Check "Run whether user is logged on or not"
3. **General** tab → Select "Run with highest privileges" (if needed)
4. **Action** tab → Edit your action
   - **Program/script**: Full path to `renewals.bat`
   - **Start in**: `C:\path\to\wealth-wise`

**Option B**: Use PowerShell script (recommended):

Create `scripts/renewals.ps1`:

```powershell
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Set default APP_URL if not set
if (-not $env:APP_URL) {
    $env:APP_URL = "http://localhost:5000"
}

# Run Python script
python scripts\process_renewals.py
```

Then in Task Scheduler:
- **Program/script**: `powershell.exe`
- **Add arguments**: `-ExecutionPolicy Bypass -File "C:\path\to\wealth-wise\scripts\renewals.ps1"`
- **Start in**: `C:\path\to\wealth-wise`

### Method 3: Python Script Only (Direct)

You can also run the Python script directly if you set environment variables manually:

```bash
# Linux/Unix
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your-password
export APP_URL=http://localhost:5000
python3 scripts/process_renewals.py

# Windows
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=your-password
set APP_URL=http://localhost:5000
python scripts\process_renewals.py
```

## Verification

### Check Logs

After the cron job runs, check the logs:

```bash
# Linux/Unix
tail -f logs/renewals.log

# Windows
type logs\renewals.log
```

### Manual Testing

Test the renewal endpoint manually:

```bash
# First, get an admin token
curl -X POST http://localhost:5000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Use the token to process renewals
curl -X POST http://localhost:5000/api/subscriptions/renewal/process \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Or use the Python script directly:
```bash
python scripts/process_renewals.py
```

## Troubleshooting

### "ADMIN_USERNAME environment variable not set"
- Ensure `.env` file exists and contains `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- For cron jobs, ensure environment variables are loaded (use `renewals.sh` wrapper)

### "Failed to authenticate"
- Verify admin credentials are correct
- Check that the Flask app is running and accessible at `APP_URL`
- Check application logs for authentication errors

### "Failed to connect to application"
- Verify `APP_URL` is correct and the application is running
- Check network connectivity
- For production, ensure `APP_URL` points to the correct domain

### Crontab Not Running
- Check cron service is running: `systemctl status cron` (Linux) or `service cron status`
- Verify cron job syntax: `crontab -l`
- Check system logs: `grep CRON /var/log/syslog` (Linux)
- Ensure absolute paths are used in crontab entries
- Ensure script has execute permissions: `chmod +x scripts/renewals.sh`

### Windows Task Scheduler Not Running
- Check Task Scheduler history for errors
- Verify Python path is correct in task action
- Ensure task is set to run whether user is logged on or not
- Check "Run with highest privileges" if needed
- Verify environment variables are set correctly

## Recommended Schedule

- **Frequency**: Daily
- **Time**: 2:00 AM (low traffic time)
- **Why**: Processes renewals before business hours, ensuring subscriptions are active when users need them

## Production Considerations

1. **Monitoring**: Set up log monitoring to alert on failures
2. **Redundancy**: Consider running multiple times per day for critical subscriptions
3. **Error Handling**: The script logs failures; monitor logs regularly
4. **Security**: Ensure `.env` file has proper permissions (not world-readable)
5. **Backup**: Keep logs for auditing subscription renewals

## Logs

Logs are written to `logs/renewals.log` and include:
- Timestamp of execution
- Authentication status
- Number of subscriptions renewed
- Any failures with subscription IDs and error messages

Rotate logs regularly to prevent disk space issues.

