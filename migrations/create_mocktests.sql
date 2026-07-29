CREATE TABLE IF NOT EXISTS MockTests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    test_date DATE NOT NULL,
    test_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MockTest_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mocktest_id INT NOT NULL,
    topic_id BIGINT NOT NULL,
    marks_obtained DECIMAL(6,2) NOT NULL DEFAULT 0,
    max_marks DECIMAL(6,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (mocktest_id) REFERENCES MockTests(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_mocktest_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id BIGINT NOT NULL,
    student_name VARCHAR(255),
    grade VARCHAR(50),
    test_name VARCHAR(255),
    test_date DATE,
    total_score VARCHAR(50),
    score_range VARCHAR(50),
    percentile VARCHAR(50),
    extracted_json JSON,
    ai_report JSON,
    file_name VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'processed') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);
