#!/bin/bash

# IdiotsMS Production Deployment Script
# This script sets up the IdiotsMS application for production deployment with Gunicorn and systemd

set -e

# Configuration
APP_NAME="idiotsms"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/opt/idiotsms"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="idiotsms"

echo "🚀 Deploying IdiotsMS to production..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root"
    exit 1
fi

# Create application directory
echo "📁 Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Copy application files
echo "📋 Copying application files..."
# Assume this script is run from the project directory
cp -r ./* $APP_DIR/

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd $APP_DIR/server
pip install -r requirements.txt

# Set permissions
echo "🔒 Setting permissions..."
chown -R $APP_USER:$APP_GROUP $APP_DIR
chmod -R 755 $APP_DIR

# Install systemd service
echo "⚙️ Installing systemd service..."
cp idiotsms.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Create environment file template
echo "📝 Creating environment file template..."
cat > $APP_DIR/.env << EOF
# IdiotsMS Production Environment Variables
# Copy this file and update with your actual values

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password_here
DB_NAME=idiotsms_accounts

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production_make_it_long_and_random
JWT_EXPIRES_IN_DAYS=7

# Server Configuration
PORT=3000
NODE_ENV=production

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
EOF

chown $APP_USER:$APP_GROUP $APP_DIR/.env
chmod 600 $APP_DIR/.env

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update $APP_DIR/.env with your actual database credentials"
echo "2. Start the service: systemctl start $SERVICE_NAME"
echo "3. Check status: systemctl status $SERVICE_NAME"
echo "4. View logs: journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔧 Management commands:"
echo "  Start: systemctl start $SERVICE_NAME"
echo "  Stop: systemctl stop $SERVICE_NAME"
echo "  Restart: systemctl restart $SERVICE_NAME"
echo "  Status: systemctl status $SERVICE_NAME"
echo "  Logs: journalctl -u $SERVICE_NAME -f"
echo "  Reload: systemctl reload $SERVICE_NAME"
