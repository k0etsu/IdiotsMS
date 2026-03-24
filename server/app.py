"""
Flask application for IdiotsMS Account Management System
"""

import os
import re
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import pymysql
from marshmallow import Schema, fields, ValidationError, validates
from email_validator import validate_email, EmailNotValidError

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_EXPIRES_IN_DAYS', 7)))
app.config['RATELIMIT_STORAGE_URL'] = 'memory://'

# Initialize extensions
# Manual CORS handling for maximum compatibility
if os.getenv('NODE_ENV') == 'development':
    # In development, allow all origins with explicit CORS middleware
    CORS(app,
         origins=["*", "http://localhost:5173"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         max_age=600)
else:
    CORS(app,
         origins=[os.getenv('PROD_URL', 'https://your-server.com')],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         max_age=600)

# Additional CORS middleware as backup
@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        # Handle preflight requests manually
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '600')
        return response

@app.after_request
def after_request(response):
    # Ensure CORS headers are present on all responses
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '600')
    return response

jwt_manager = JWTManager(app)

# JWT error handler
@jwt_manager.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"JWT expired: {jwt_payload}")
    return jsonify({'error': 'Token has expired'}), 401

@jwt_manager.invalid_token_loader
def invalid_token_callback(error):
    print(f"JWT invalid: {error}")
    return jsonify({'error': 'Invalid token'}), 401

@jwt_manager.unauthorized_loader
def missing_token_callback(error):
    print(f"JWT missing: {error}")
    return jsonify({'error': 'Authorization token is required'}), 401

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{os.getenv('RATE_LIMIT_MAX_REQUESTS', '100')}/{int(os.getenv('RATE_LIMIT_WINDOW_MS', '900000'))//1000} seconds"]
)

# Request logging middleware
@app.before_request
def log_request():
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    if request.method == 'OPTIONS':
        print(f"OPTIONS request detected")
    return None

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'idiotsms_accounts'),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

# Validation schemas
class RegistrationSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: 3 <= len(x) <= 12)
    password = fields.Str(required=True, validate=lambda x: 5 <= len(x) <= 12)
    confirm_password = fields.Str(required=True)

    @validates('username')
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username can only contain letters, numbers, and underscores')

    @validates('confirm_password')
    def validate_confirm_password(self, value):
        if value != self.context.get('password'):
            raise ValidationError('Password confirmation does not match')

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: 4 <= len(x) <= 12)
    password = fields.Str(required=True, validate=lambda x: 5 <= len(x) <= 12)

class ChangePasswordSchema(Schema):
    currentPassword = fields.Str(required=True, validate=lambda x: 5 <= len(x) <= 12)
    newPassword = fields.Str(required=True, validate=lambda x: 5 <= len(x) <= 12)
    confirmNewPassword = fields.Str(required=True)

    @validates('newPassword')
    def validate_newPassword(self, value):
        if value != self.context.get('confirmNewPassword'):
            raise ValidationError('New password confirmation does not match')

# Validation helpers
def validate_username(username):
    return re.match(r'^[a-zA-Z0-9]{3,12}$', username) is not None

def validate_password(password):
    return re.match(r'^[a-zA-Z0-9@$!%*?&]{5,12}$', password) is not None

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify({'errors': err.messages}), 400

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Too many requests from this IP, please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/register', methods=['POST'])
@limiter.limit("5/minute")  # Stricter limit for registration
def register():
    try:
        # Validate input
        schema = RegistrationSchema()
        data = schema.load(request.json)

        username = data['username'].strip()
        password = data['password']

        # Additional validation
        if not validate_username(username):
            return jsonify({'error': 'Username can only contain letters and numbers'}), 400

        if not validate_password(password):
            return jsonify({
                'error': 'Password must be 5-12 characters with at least one uppercase letter, one lowercase letter, and one number'
            }), 400

        # Check if username already exists
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM accounts WHERE name = %s", (username))
                existing_user = cursor.fetchone()

                if existing_user:
                    return jsonify({'error': 'Username already exists'}), 409

                # Hash password and create account
                hashed_password = hash_password(password)
                cursor.execute(
                    "INSERT INTO accounts (name, password, createdat) VALUES (%s, %s, NOW())",
                    (username, hashed_password)
                )
                user_id = cursor.lastrowid
                conn.commit()

                # Create JWT token
                access_token = create_access_token(
                    identity={'id': user_id, 'username': username}
                )

                return jsonify({
                    'message': 'Account created successfully',
                    'token': access_token,
                    'user': {'id': user_id, 'username': username}
                }), 201

        finally:
            conn.close()

    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("10/minute")  # Stricter limit for login attempts
def login():
    try:
        # Validate input
        schema = LoginSchema()
        data = schema.load(request.json)

        username = data['username'].strip()
        password = data['password']

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, password FROM accounts WHERE name = %s",
                    (username)
                )
                user = cursor.fetchone()

                if not user or not verify_password(password, user['password']):
                    return jsonify({'error': 'Invalid username or password'}), 401

                # Create JWT token
                token_identity = str(user['id'])  # JWT identity must be a string (user ID)
                print(f"Creating JWT with identity: {token_identity}")  # Debug line
                access_token = create_access_token(identity=token_identity)
                print(f"JWT token created successfully")  # Debug line

                return jsonify({
                    'message': 'Login successful',
                    'token': access_token,
                    'user': {'id': user['id'], 'username': user['name']}
                })

        finally:
            conn.close()

    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = get_jwt_identity()
        print(f"JWT Identity: {current_user}")  # Debug line
        print(f"JWT Identity type: {type(current_user)}")  # Debug line

        # JWT identity is now a string (user ID), not a dictionary
        if not current_user or not isinstance(current_user, str):
            print(f"Invalid JWT identity: {current_user}")
            return jsonify({'error': 'Invalid token'}), 401

        # Convert to integer for database query
        try:
            user_id = int(current_user)
        except (ValueError, TypeError):
            print(f"Invalid user ID in JWT: {current_user}")
            return jsonify({'error': 'Invalid token structure'}), 401

        print(f"User ID extracted: {user_id}")  # Debug line
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, createdat FROM accounts WHERE id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                print(f"Database user found: {user}")  # Debug line

                if not user:
                    return jsonify({'error': 'User not found'}), 404

                return jsonify({'user': user})

        finally:
            conn.close()

    except Exception as e:
        print(f"Profile error: {e}")
        print(f"Error type: {type(e)}")  # Debug line
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")  # Debug line
        return jsonify({'error': 'Internal server error'}), 500
    print(f"Debug - Headers: {dict(request.headers)}")
    print(f"Debug - URL: {request.url}")
    return jsonify({
        'method': request.method,
        'headers': dict(request.headers),
        'url': request.url
    })

@app.route('/api/change-password', methods=['POST'])
@jwt_required()
@limiter.limit("3/minute")  # Very strict limit for password changes
def change_password():
    try:
        user_id = get_jwt_identity()

        # Validate input
        schema = ChangePasswordSchema()
        data = schema.load(request.json)

        current_password = data['currentPassword']
        new_password = data['newPassword']

        # Additional validation for new password
        if not validate_password(new_password):
            return jsonify({
                'error': 'New password must be 5-12 characters with at least one uppercase letter, one lowercase letter, and one number'
            }), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get current user password
                cursor.execute("SELECT password FROM accounts WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    return jsonify({'error': 'User not found'}), 404

                # Verify current password
                if not verify_password(current_password, user_data['password']):
                    return jsonify({'error': 'Current password is incorrect'}), 401

                # Check if new password is the same as current
                if verify_password(new_password, user_data['password']):
                    return jsonify({'error': 'New password must be different from current password'}), 400

                # Hash new password and update
                hashed_new_password = hash_password(new_password)
                cursor.execute(
                    "UPDATE accounts SET password = %s WHERE id = %s",
                    (hashed_new_password, user_id)
                )
                conn.commit()

                return jsonify({'message': 'Password updated successfully'})

        finally:
            conn.close()

    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        print(f"Change password error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV') == 'development'
    print(f"Starting Flask server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"CORS enabled: {os.getenv('NODE_ENV') == 'development'}")
    app.run(host='0.0.0.0', port=port, debug=debug)
