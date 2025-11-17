#!/bin/bash
# Azure deployment script for STEWARD
# This script helps set up Azure App Service for Flask deployment

echo "🚀 STEWARD Azure Deployment Helper"
echo "=================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "⚠️  Azure CLI not found. Installing instructions:"
    echo "   Windows: https://aka.ms/installazurecliwindows"
    echo "   Mac: brew install azure-cli"
    echo "   Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

echo "✅ Azure CLI found"
echo ""

# Login check
echo "Checking Azure login status..."
az account show &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please login to Azure:"
    az login
fi

echo "✅ Logged in to Azure"
echo ""

# Get user input
read -p "Enter your app name (must be globally unique): " APP_NAME
read -p "Enter resource group name: " RESOURCE_GROUP
read -p "Enter region (e.g., eastus, westeurope): " REGION
read -p "Enter PostgreSQL server name: " DB_SERVER_NAME
read -p "Enter PostgreSQL admin username: " DB_USERNAME
read -s -p "Enter PostgreSQL admin password: " DB_PASSWORD
echo ""

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $REGION

# Create App Service Plan (Free F1)
echo "Creating App Service Plan (Free F1)..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku FREE \
    --is-linux

# Create Web App
echo "Creating Web App..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON:3.11"

# Configure app settings
echo "Configuring app settings..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        FLASK_ENV=production \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true

# Set startup command
echo "Setting startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "gunicorn --bind 0.0.0.0:8000 app:app"

# Create PostgreSQL Flexible Server (Free tier)
echo "Creating PostgreSQL database..."
az postgres flexible-server create \
    --name $DB_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $REGION \
    --admin-user $DB_USERNAME \
    --admin-password $DB_PASSWORD \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --version 14 \
    --storage-size 32 \
    --public-access 0.0.0.0

# Get database connection string
DB_CONNECTION_STRING="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com/postgres?sslmode=require"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Set DATABASE_URL in App Service:"
echo "   az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings DATABASE_URL='$DB_CONNECTION_STRING'"
echo ""
echo "2. Set other environment variables (SECRET_KEY, JWT_SECRET_KEY, etc.)"
echo ""
echo "3. Connect GitHub for continuous deployment:"
echo "   - Go to Azure Portal → Your App Service → Deployment Center"
echo "   - Connect your GitHub repository"
echo ""
echo "4. Your app will be available at: https://${APP_NAME}.azurewebsites.net"
echo ""

