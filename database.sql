-- IdiotsMS Account Management Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS idiotsms_accounts CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE idiotsms_accounts;

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id             INT          NOT NULL AUTO_INCREMENT,
    `name`         VARCHAR(13)  NOT NULL DEFAULT '',
    password       VARCHAR(128) NOT NULL DEFAULT '',
    pin            VARCHAR(10)  NOT NULL DEFAULT '',
    pic            VARCHAR(26)  NOT NULL DEFAULT '',
    loggedin       TINYINT      NOT NULL DEFAULT '0',
    lastlogin      TIMESTAMP    NULL     DEFAULT NULL,
    createdat      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    birthday       DATE         NOT NULL DEFAULT '2005-05-11',
    banned         TINYINT      NOT NULL DEFAULT '0',
    banreason      TEXT,
    macs           TINYTEXT,
    nxCredit       INT                   DEFAULT NULL,
    maplePoint     INT                   DEFAULT NULL,
    nxPrepaid      INT                   DEFAULT NULL,
    characterslots TINYINT      NOT NULL DEFAULT '3',
    gender         TINYINT      NOT NULL DEFAULT '10',
    tempban        TIMESTAMP    NOT NULL DEFAULT '2005-05-11 00:00:00',
    greason        TINYINT      NOT NULL DEFAULT '0',
    tos            TINYINT      NOT NULL DEFAULT '0',
    sitelogged     TEXT,
    webadmin       INT                   DEFAULT '0',
    nick           VARCHAR(20)           DEFAULT NULL,
    mute           INT                   DEFAULT '0',
    email          VARCHAR(45)           DEFAULT NULL,
    ip             TEXT,
    rewardpoints   INT          NOT NULL DEFAULT '0',
    votepoints     INT          NOT NULL DEFAULT '0',
    hwid           VARCHAR(12)  NOT NULL DEFAULT '',
    language       INT          NOT NULL DEFAULT '2',
    PRIMARY KEY (id),
    UNIQUE KEY `name` (`name`),
    KEY ranking1 (id, banned),
    INDEX (id, `name`),
    INDEX (id, nxCredit, maplePoint, nxPrepaid)
) ENGINE=InnoDB;

-- Account login attempts for security tracking
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(12) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username_attempts (username, attempted_at),
    INDEX idx_ip_attempts (ip_address, attempted_at)
) ENGINE=InnoDB;

-- Password reset tokens (if needed in future)
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sample data (optional - for testing)
-- INSERT INTO accounts (name, password) VALUES
-- ('admin', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm'); -- password: Admin123

-- Note: The hashed password above is for 'Admin123' (8-12 chars, uppercase, lowercase, number)
-- Note: This uses the 'name' field instead of 'username' to match IdiotsMS server structure
