-- =================================================
-- Database setup SQL script for CyberPatriot Runbook
-- =================================================

-- 1. Create database
CREATE DATABASE IF NOT EXISTS cyberpatriot_runbook
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cyberpatriot_runbook;

-- 2. Create users table first (needed for foreign keys)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('member','captain','coach','admin','pending') NOT NULL DEFAULT 'pending',
    team_id INT,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_email (email)
);

-- 3. Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team_id CHAR(7) NOT NULL UNIQUE, -- Format: NN-NNNN
    division ENUM('CivilAirPatrol','JROTC','HighSchool','Open','MiddleSchool') NOT NULL,
    created_by_user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_team_id (team_id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add foreign key to users table now that teams table exists
ALTER TABLE users ADD CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL;

-- 4. Team join requests table (for coaches/admins joining same team)
CREATE TABLE IF NOT EXISTS team_join_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    requester_user_id INT NOT NULL,
    team_creator_user_id INT NOT NULL,
    status ENUM('PENDING','APPROVED','REJECTED') NOT NULL DEFAULT 'PENDING',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_team_requester (team_id, requester_user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (requester_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (team_creator_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Team members table (for approval workflow)
CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT NOT NULL,
    status ENUM('approved','pending','rejected') NOT NULL DEFAULT 'pending',
    assigned_role ENUM('member','captain','coach') NOT NULL DEFAULT 'member',
    approved_by INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_team (user_id, team_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 6. Checklists table
CREATE TABLE IF NOT EXISTS checklists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'General',
    created_by INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 7. Checklist items table
CREATE TABLE IF NOT EXISTS checklist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checklist_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description MEDIUMTEXT,
    `order` INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
);

-- 8. Checklist status table
CREATE TABLE IF NOT EXISTS checklist_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checklist_item_id INT NOT NULL,
    status ENUM('pending','complete','incomplete','skipped') NOT NULL DEFAULT 'pending',
    notes MEDIUMTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_item (user_id, checklist_item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (checklist_item_id) REFERENCES checklist_items(id) ON DELETE CASCADE
);

-- 9. READMEs table
CREATE TABLE IF NOT EXISTS readmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    os_type ENUM('Windows','Linux','Cisco','Other') NOT NULL,
    content LONGTEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Notes table
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    note_type ENUM('General','Points','PasswordChange','Misc') DEFAULT 'General',
    is_encrypted BOOLEAN DEFAULT FALSE,
    encryption_key_salt VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 11. Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    KEY idx_user_id (user_id),
    KEY idx_created_at (created_at)
);

-- 12. System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(255) NOT NULL UNIQUE,
    setting_value TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 13. Indexes for performance
CREATE INDEX idx_checklist_category ON checklists(category);
CREATE INDEX idx_readme_team ON readmes(team_id);
CREATE INDEX idx_note_team ON notes(team_id);

-- 14. Create application MySQL user
CREATE USER IF NOT EXISTS 'app'@'localhost' IDENTIFIED BY '1L!k3my9@55w0rd';
GRANT ALL PRIVILEGES ON cyberpatriot_runbook.* TO 'app'@'localhost';
FLUSH PRIVILEGES;

-- 15. Insert sample data for testing
-- Sample admin user first (password: 'Admin@123' hashed with bcrypt)
-- Note: You must hash passwords with bcrypt in Python before inserting
-- This is a placeholder - update with actual hashed password
INSERT IGNORE INTO users (name, email, password_hash, role, is_approved, is_active) VALUES 
('Admin User', 'admin@cyberpatriot.local', '$2b$12$placeholder', 'admin', TRUE, TRUE);

-- Sample team (created by the admin user - id=1)
INSERT IGNORE INTO teams (name, team_id, division, created_by_user_id) VALUES 
('Blue Squadron', '01-0001', 'CivilAirPatrol', 1);

-- 16. Show tables and summary
SHOW TABLES;
SELECT 'Database setup complete!' as status;
SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'cyberpatriot_runbook';
