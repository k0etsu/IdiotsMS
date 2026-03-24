const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://yourdomain.com'] 
    : ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Database connection pool
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'maplestory_accounts',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// JWT middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Validation helpers
const validateUsername = (username) => {
  return /^[a-zA-Z0-9_]{3,12}$/.test(username);
};

const validatePassword = (password) => {
  // At least 8 characters, max 12, at least one uppercase, one lowercase, one number
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,12}$/.test(password);
};

// Routes
app.post('/api/register', [
  body('username').trim().isLength({ min: 3, max: 12 }).withMessage('Username must be 3-12 characters'),
  body('password').isLength({ min: 8, max: 12 }).withMessage('Password must be 8-12 characters'),
  body('confirmPassword').custom((value, { req }) => {
    if (value !== req.body.password) {
      throw new Error('Password confirmation does not match');
    }
    return true;
  })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password } = req.body;

    // Additional validation
    if (!validateUsername(username)) {
      return res.status(400).json({ error: 'Username can only contain letters, numbers, and underscores' });
    }

    if (!validatePassword(password)) {
      return res.status(400).json({ 
        error: 'Password must be 8-12 characters with at least one uppercase letter, one lowercase letter, and one number' 
      });
    }

    // Check if username already exists
    const [existingUsers] = await pool.execute(
      'SELECT id FROM accounts WHERE username = ?',
      [username]
    );

    if (existingUsers.length > 0) {
      return res.status(409).json({ error: 'Username already exists' });
    }

    // Hash password
    const saltRounds = 12;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Create account
    const [result] = await pool.execute(
      'INSERT INTO accounts (username, password, created_at, updated_at) VALUES (?, ?, NOW(), NOW())',
      [username, hashedPassword]
    );

    // Generate JWT token
    const token = jwt.sign(
      { id: result.insertId, username },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.status(201).json({
      message: 'Account created successfully',
      token,
      user: { id: result.insertId, username }
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/login', [
  body('username').trim().isLength({ min: 3, max: 12 }).withMessage('Username must be 3-12 characters'),
  body('password').isLength({ min: 8, max: 12 }).withMessage('Password must be 8-12 characters')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password } = req.body;

    // Find user
    const [users] = await pool.execute(
      'SELECT id, username, password FROM accounts WHERE username = ?',
      [username]
    );

    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid username or password' });
    }

    const user = users[0];

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid username or password' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { id: user.id, username: user.username },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.json({
      message: 'Login successful',
      token,
      user: { id: user.id, username: user.username }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/change-password', authenticateToken, [
  body('currentPassword').isLength({ min: 8, max: 12 }).withMessage('Current password must be 8-12 characters'),
  body('newPassword').isLength({ min: 8, max: 12 }).withMessage('New password must be 8-12 characters'),
  body('confirmNewPassword').custom((value, { req }) => {
    if (value !== req.body.newPassword) {
      throw new Error('New password confirmation does not match');
    }
    return true;
  })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { currentPassword, newPassword } = req.body;
    const userId = req.user.id;

    // Additional validation for new password
    if (!validatePassword(newPassword)) {
      return res.status(400).json({ 
        error: 'New password must be 8-12 characters with at least one uppercase letter, one lowercase letter, and one number' 
      });
    }

    // Get current user password
    const [users] = await pool.execute(
      'SELECT password FROM accounts WHERE id = ?',
      [userId]
    );

    if (users.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Verify current password
    const isValidPassword = await bcrypt.compare(currentPassword, users[0].password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Current password is incorrect' });
    }

    // Check if new password is the same as current
    const isSamePassword = await bcrypt.compare(newPassword, users[0].password);
    if (isSamePassword) {
      return res.status(400).json({ error: 'New password must be different from current password' });
    }

    // Hash new password
    const saltRounds = 12;
    const hashedNewPassword = await bcrypt.hash(newPassword, saltRounds);

    // Update password
    await pool.execute(
      'UPDATE accounts SET password = ?, updated_at = NOW() WHERE id = ?',
      [hashedNewPassword, userId]
    );

    res.json({ message: 'Password updated successfully' });

  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/profile', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const [users] = await pool.execute(
      'SELECT id, username, created_at, updated_at FROM accounts WHERE id = ?',
      [userId]
    );

    if (users.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user: users[0] });

  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
