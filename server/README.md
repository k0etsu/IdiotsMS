# Flask Server for IdiotsMS

This directory contains the Flask backend for the IdiotsMS Account Management System, managed with `uv`.

## Quick Start

```bash
# Install dependencies
uv sync

# Run development server
uv run run.py

# Run production server
uv run app.py
```

## Project Structure

- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `run.py` - Development server runner
- `pyproject.toml` - uv project configuration
- `.python-version` - Python version specification

## uv Commands

```bash
# Install all dependencies
uv sync

# Install only production dependencies
uv sync --no-dev

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name

# Update dependencies
uv sync --upgrade

# Run any command in the virtual environment
uv run python -c "import flask; print(flask.__version__)"

# List installed packages
uv pip list
```

## Development

The project uses uv for modern Python package management:

- **Fast dependency resolution** - uv is 10-100x faster than pip
- **Automatic virtual environment** - Creates `.venv` automatically
- **Lock file** - `uv.lock` ensures reproducible builds
- **Modern configuration** - Uses `pyproject.toml` for all project metadata

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=maplestory_accounts
JWT_SECRET=your_jwt_secret
PORT=3000
NODE_ENV=development
```

## Testing

```bash
# Install development dependencies
uv sync --dev

# Run tests (when tests are added)
uv run pytest
```

## Code Quality

```bash
# Format code with black
uv run black .

# Lint with flake8
uv run flake8 .

# Type check with mypy
uv run mypy .
```
