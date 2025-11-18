-- Initialize the database with the comments table
-- This script runs automatically when the database container starts for the first time

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on created_at for faster ordering
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);

-- Insert a welcome message
INSERT INTO comments (content, created_at) VALUES 
('Welcome to the Anonymous Forum! This is a LAN-based discussion board where you can share your thoughts freely.', CURRENT_TIMESTAMP);
