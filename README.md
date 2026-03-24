# IdiotsMS Account Management System

A modern Vue 3 frontend with Flask backend for managing IdiotsMS server accounts with MySQL database integration.

## Features

- **User Registration**: Create new accounts with username (3-12 chars) and password (8-12 chars)
- **User Login**: Secure authentication with JWT tokens
- **Password Management**: Change passwords with modern security practices
- **Password Strength Validation**: Real-time password strength indicators
- **Modern UI**: Beautiful, responsive design with Vue 3
- **Security**: Rate limiting, CORS protection, input validation, bcrypt hashing

## Requirements

- Python 3.12+
- uv (Python package manager)
- Node.js 16+
- MySQL 8.0+
- npm or yarn

## Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (alternative)
pip install uv
```

### 2. Database Setup

Create the MySQL database and tables:

```bash
mysql -u root -p < database.sql
```

### 3. Environment Configuration

#### Quick Setup (Recommended)

Run the setup script to create both environment files:

```bash
npm run setup-env
```

Then edit both `.env` files with your configuration.

#### Manual Setup

**Backend (.env)**

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Update `.env` with your database configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=idiotsms_accounts

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here_make_it_long_and_random
JWT_EXPIRES_IN_DAYS=7

# Server Configuration
PORT=3000
NODE_ENV=development

# Frontend Configuration (for CORS)
VITE_PORT=5173

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

**Note:** The `VITE_PORT` in the server `.env` should match the `VITE_PORT` in your client `.env` file to ensure proper CORS configuration.

**Frontend (.env)**

Copy `.env.example` to `.env` in the client directory:

```bash
cp client/.env.example client/.env
```

**Important:** The frontend environment variables must match the server configuration from the root `.env` file. Make sure the `VITE_PORT` and `VITE_API_BASE_URL` use the same port as the server's `PORT`.

Update `client/.env` to match your server configuration:

```bash
# API Configuration - must match server PORT from root .env
VITE_API_BASE_URL=http://localhost:3000/api
VITE_PORT=3000

# Development settings
VITE_NODE_ENV=development
```

**Example:** If your server `.env` has `PORT=8080`, then your client `.env` should have:
```bash
VITE_API_BASE_URL=http://localhost:8080/api
VITE_PORT=8080
```

### 4. Install Dependencies

```bash
# Install Python dependencies with uv
npm run install-python

# Install Node.js dependencies for client
npm run install-client

# Or install both at once
npm run install-deps
```

### 5. Start the Application

Development mode (starts both server and client):

```bash
npm run dev
```

Or start them separately:

```bash
# Start Flask server (development)
npm run server

# Start Vue client (in another terminal)
npm run client
```

Production mode:

```bash
# Build the client
npm run build

# Start Flask server (production)
npm start
```

## API Endpoints

### Authentication
- `POST /api/register` - Create new account
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile (requires auth)
- `POST /api/change-password` - Change password (requires auth)
- `GET /api/health` - Health check

## Password Requirements

- **Username**: 3-12 characters, alphanumeric + underscores only
- **Password**: 8-12 characters with:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - Optional special characters (@$!%*?&)

## Security Features

- **Password Hashing**: bcrypt with 12 salt rounds
- **JWT Authentication**: Secure token-based auth using Flask-JWT-Extended
- **Rate Limiting**: Configurable limits per endpoint
- **Input Validation**: Comprehensive validation using Marshmallow schemas
- **CORS Protection**: Configured for production and development
- **SQL Injection Protection**: Using parameterized queries with PyMySQL
- **Security Headers**: Flask-CORS and proper middleware configuration

## Project Structure

```
├── client/                 # Vue 3 frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── stores/         # Pinia stores
│   │   └── main.js         # App entry point
│   ├── package.json
│   └── vite.config.js
├── server/                 # Flask backend
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   ├── run.py             # Development server runner
│   ├── pyproject.toml     # uv project configuration
│   ├── .python-version    # Python version specification
│   └── requirements.txt   # Legacy requirements (optional)
├── database.sql           # MySQL schema
├── package.json           # Root dependencies (for npm scripts)
└── README.md
```

## Usage

1. Navigate to `http://localhost:5173` for the frontend
2. Register a new account
3. Login with your credentials
4. Access the dashboard to view account info and change password

## Development

The development server starts both the backend (port 3000) and frontend (port 5173) concurrently with hot reload enabled.

## Production Deployment

1. Build the client: `npm run build`
2. Set production environment variables
3. Start the server: `npm start`

The built frontend will be served from the backend as static files.

## Flask vs Node.js

This version uses Flask instead of Node.js/Express for the backend while maintaining the same API endpoints and functionality. Key differences:

- **Python ecosystem** with PyMySQL for database connectivity
- **Flask-JWT-Extended** for JWT token management
- **Marshmallow** for input validation and serialization
- **Flask-Limiter** for rate limiting
- **bcrypt** for password hashing (same algorithm, different library)
- **uv** for modern Python package management and virtual environments

## About IdiotsMS

IdiotsMS is a private server that provides an enhanced gaming experience. This account management system handles user registration, authentication, and password management for the IdiotsMS server.

## uv Package Management

This project uses `uv` for Python dependency management:

- **Fast dependency resolution** - uv is significantly faster than pip
- **Automatic virtual environment** - uv creates and manages .venv automatically
- **Modern project configuration** - Uses `pyproject.toml` for dependency specification
- **Development dependencies** - Separate dev dependencies for testing and linting
- **Python version pinning** - `.python-version` ensures consistent Python version

### uv Commands

```bash
# Install dependencies
uv sync

# Run application
uv run app.py

# Add new dependency
uv add flask-sqlalchemy

# Add dev dependency
uv add --dev pytest

# Update dependencies
uv sync --upgrade
```

## License

MIT
