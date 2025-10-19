-- Add OAuth columns to existing admins table
-- Run this script to update your existing database

-- Add is_admin column if it doesn't exist
ALTER TABLE admins ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT TRUE;

-- Add OAuth columns if they don't exist
ALTER TABLE admins ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255);
ALTER TABLE admins ADD COLUMN IF NOT EXISTS access_token TEXT;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS refresh_token TEXT;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMPTZ;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Update existing admin record to have is_admin = TRUE
UPDATE admins SET is_admin = TRUE WHERE is_admin IS NULL;
