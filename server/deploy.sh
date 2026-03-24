#!/bin/bash

# IdiotsMS Production Deployment Script
# This script sets up the IdiotsMS application using UV for package and venv management

set -e

# Configuration
APP_NAME="idiotsms"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/opt/idiotsms"
SERVICE_NAME="idiotsms"

echo "🚀 Deploying IdiotsMS to production with UV..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root"
    exit 1
fi

# Create application directory
echo "📁 Creating application directory..."
mkdir -p $APP_DIR

# Copy application files
echo "📋 Copying application files..."
cp -r ./* $APP_DIR/

# Create UV virtual environment
echo "🐍 Creating UV virtual environment..."
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
echo "Using uv for virtual environment management..."
cd $APP_DIR/server
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
echo "source $APP_DIR/server/.venv/bin/activate" > $APP_DIR/activate.sh
chmod +x $APP_DIR/activate.sh

# Install Python dependencies
echo "📦 Installing Python dependencies with UV..."
cd $APP_DIR/server
echo "Using uv for dependency installation..."
uv sync

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

echo "✅ UV Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update $APP_DIR/.env with your actual database credentials"
echo "2. Start service: systemctl start $SERVICE_NAME"
echo "3. Check status: systemctl status $SERVICE_NAME"
echo "4. View logs: journalctl -u $SERVICE_NAME -f"
echo ""
echo "🧧 Management commands:"
echo "  Start: systemctl start $SERVICE_NAME"
echo "  Stop: systemctl stop $SERVICE_NAME"
echo "  Restart: systemctl restart $SERVICE_NAME"
echo "  Status: systemctl status $SERVICE_NAME"
echo "  Logs: journalctl -u $SERVICE_NAME -f"
echo "  Reload: systemctl reload $SERVICE_NAME"
echo ""
echo "🔧 UV-specific commands:"
echo "  Update deps: cd $APP_DIR/server && uv sync"
echo "  Add package: cd $APP_DIR/server && uv add package-name"
echo "  Remove package: cd $APP_DIR/server && uv remove package-name"
echo "  Lock deps: cd $APP_DIR/server && uv lock"
echo "  Activate: source $APP_DIR/activate.sh"
echo ""
echo "🌐 Deployment URL: http://$(hostname -I):${PORT:-3000}"
