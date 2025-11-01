# PowerShell script for Windows Task Scheduler
# This script loads environment variables from .env and runs the renewal processor

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

# Load .env file
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove quotes if present
            if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                $value = $matches[1]
            }
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Error ".env file not found in $projectPath"
    exit 1
}

# Set default APP_URL if not set
if (-not $env:APP_URL) {
    $env:APP_URL = "http://localhost:5000"
}

# Ensure required variables are set
if (-not $env:ADMIN_USERNAME -or -not $env:ADMIN_PASSWORD) {
    Write-Error "ADMIN_USERNAME and ADMIN_PASSWORD must be set in .env file"
    exit 1
}

# Run Python script
python scripts\process_renewals.py

# Exit with the Python script's exit code
exit $LASTEXITCODE

