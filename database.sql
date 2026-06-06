CREATE DATABASE monitoring_db;

USE monitoring_db;

-- ======================
-- USERS
-- ======================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    last_login DATETIME NULL
);

-- ======================
-- MONITORING LOGS
-- ======================

CREATE TABLE monitoring_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cpu_usage FLOAT,
    ram_usage FLOAT,
    disk_usage FLOAT,
    swap_usage FLOAT,
    active_users INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ======================
-- ALERTS
-- ======================

CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    value FLOAT,
    status VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ======================
-- PROCESS LOGS
-- ======================

CREATE TABLE process_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255),
    pid INT,
    admin VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ======================
-- LINUX USERS
-- ======================

CREATE TABLE linux_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    last_login DATETIME NULL,
    status VARCHAR(20)
);

-- ======================
-- ACTIVITY LOGS
-- ======================

CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255),
    admin VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
