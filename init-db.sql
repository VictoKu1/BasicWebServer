-- Initialize the database with the comments table
-- This script runs automatically when the database container starts for the first time

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL CHECK (char_length(content) <= 5000),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on created_at for faster ordering
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);

-- Insert a welcome message
INSERT INTO comments (content, created_at) VALUES 
('Welcome to the Anonymous Forum! This is a LAN-based discussion board where you can share your thoughts freely.', CURRENT_TIMESTAMP);

-- Least-privilege application user
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'forumapp') THEN
      CREATE ROLE forumapp LOGIN PASSWORD 'forumapppass';
   END IF;
END
$$;

GRANT CONNECT ON DATABASE forumdb TO forumapp;
GRANT USAGE ON SCHEMA public TO forumapp;
GRANT SELECT, INSERT ON TABLE comments TO forumapp;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO forumapp;

-- Ensure future tables also grant minimal privileges to forumapp
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO forumapp;
