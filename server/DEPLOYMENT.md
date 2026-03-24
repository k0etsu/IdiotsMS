# IdiotsMS Production Deployment Guide

This guide covers deploying IdiotsMS to production using Gunicorn and systemd.

## 📋 Prerequisites

- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- MySQL 8.0+
- Root access to server
- Domain name (e.g., maplestory.yamanote.co)

## 🚀 Quick Deployment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd idiots-ms
   ```

2. **Run the deployment script:**
   ```bash
   sudo chmod +x server/deploy.sh
   sudo server/deploy.sh
   ```

3. **Configure environment:**
   ```bash
   sudo nano /opt/idiotsms/.env
   ```

4. **Start the service:**
   ```bash
   sudo systemctl start idiotsms
   ```

## ⚙️ Manual Deployment

If you prefer to deploy manually:

### 1. Setup Application Directory
```bash
sudo mkdir -p /opt/idiotsms
sudo cp -r ./* /opt/idiotsms/
cd /opt/idiotsms
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
cd server
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
sudo nano .env
```

Add your production configuration:
```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
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
```

### 4. Setup Systemd Service
```bash
sudo cp idiotsms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable idiotsms
```

### 5. Start Service
```bash
sudo systemctl start idiotsms
sudo systemctl status idiotsms
```

## 🔧 Service Management

### Start/Stop/Restart
```bash
# Start
sudo systemctl start idiotsms

# Stop
sudo systemctl stop idiotsms

# Restart
sudo systemctl restart idiotsms

# Reload (graceful restart)
sudo systemctl reload idiotsms
```

### Status and Logs
```bash
# Check status
sudo systemctl status idiotsms

# View logs
sudo journalctl -u idiotsms -f

# View last 100 lines
sudo journalctl -u idiotsms -n 100
```

## 🔒 SSL/HTTPS Setup

### Using Nginx Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Create Nginx config:**
   ```bash
   sudo nano /etc/nginx/sites-available/maplestory.yamanote.co
   ```

```nginx
server {
    listen 80;
    server_name maplestory.yamanote.co;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/maplestory.yamanote.co /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Using Certbot for SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d maplestory.yamanote.co

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring

### Health Check Endpoint
The application includes a health check endpoint:
```bash
curl https://maplestory.yamanote.co/api/health
```

### Log Monitoring
```bash
# Application logs
sudo journalctl -u idiotsms -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Updates

### Update Application
```bash
cd /opt/idiotsms
sudo systemctl stop idiotsms
git pull origin main
source venv/bin/activate
cd server
pip install -r requirements.txt
sudo systemctl start idiotsms
```

## 🐛 Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   sudo journalctl -u idiotsms -n 50
   ```

2. **Database connection errors:**
   - Check .env file permissions
   - Verify MySQL is running
   - Test database credentials

3. **Port already in use:**
   ```bash
   sudo netstat -tlnp | grep :3000
   sudo systemctl stop idiotsms
   sudo systemctl start idiotsms
   ```

4. **Permission errors:**
   ```bash
   sudo chown -R www-data:www-data /opt/idiotsms
   sudo chmod -R 755 /opt/idiotsms
   ```

## 🔐 Security Recommendations

1. **Firewall configuration:**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Database security:**
   - Use strong MySQL password
   - Create dedicated database user
   - Limit database user permissions

3. **Application security:**
   - Change default JWT secret
   - Use HTTPS in production
   - Regularly update dependencies
   - Monitor logs for suspicious activity
