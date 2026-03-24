#!/usr/bin/env python3
"""
Gunicorn configuration for IdiotsMS production deployment
"""

import os
import multiprocessing
from dotenv import load_dotenv

load_dotenv()

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '3000')}"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Timeout settings
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'idiotsms'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if needed)
# keyfile = '/path/to/ssl/key.pem'
# certfile = '/path/to/ssl/cert.pem'

# UV environment
raw_env = [
    'PORT=' + os.getenv('PORT', '3000'),
    'NODE_ENV=' + os.getenv('NODE_ENV', 'production'),
    'DB_HOST=' + os.getenv('DB_HOST', 'localhost'),
    'DB_USER=' + os.getenv('DB_USER', 'root'),
    'DB_PASSWORD=' + os.getenv('DB_PASSWORD', ''),
    'DB_NAME=' + os.getenv('DB_NAME', 'idiotsms_accounts'),
    'JWT_SECRET=' + os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-this-in-production'),
    'JWT_EXPIRES_IN_DAYS=' + os.getenv('JWT_EXPIRES_IN_DAYS', '7'),
    'RATE_LIMIT_WINDOW_MS=' + os.getenv('RATE_LIMIT_WINDOW_MS', '900000'),
    'RATE_LIMIT_MAX_REQUESTS=' + os.getenv('RATE_LIMIT_MAX_REQUESTS', '100')
]
