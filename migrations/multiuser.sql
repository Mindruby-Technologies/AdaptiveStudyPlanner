-- Step 1: Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Insert default admin user (password: admin123)
INSERT INTO users (username, email, password_hash) VALUES (
    'admin',
    'admin@studyplanner.com',
    '$2b$12$KIXtCDgDaGBL9N8Qz1v5OuQwX9Y2mZ3nP4rS6tU7vW8xA0bC1dE2f'
);

-- Step 3: Add user_id to all tables (default 1 = existing admin, preserves existing data)
ALTER TABLE tests ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_tests_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE subjects ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_subjects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE MockTests ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_mocktests_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE ai_mocktest_reports ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_ai_reports_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE schedule_entries ADD COLUMN user_id INT NOT NULL DEFAULT 1,
    ADD CONSTRAINT fk_schedule_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
