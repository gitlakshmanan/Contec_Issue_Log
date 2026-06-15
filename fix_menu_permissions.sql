-- SQL script to add missing menu permission columns to base_userprofile table
-- Run this in your database to fix the migration issue

ALTER TABLE base_userprofile 
ADD COLUMN can_access_issues BOOLEAN NOT NULL DEFAULT 1;

ALTER TABLE base_userprofile 
ADD COLUMN can_access_parts BOOLEAN NOT NULL DEFAULT 0;

ALTER TABLE base_userprofile 
ADD COLUMN can_access_cr BOOLEAN NOT NULL DEFAULT 0;

ALTER TABLE base_userprofile 
ADD COLUMN can_access_tasks BOOLEAN NOT NULL DEFAULT 1;

ALTER TABLE base_userprofile 
ADD COLUMN can_access_reports BOOLEAN NOT NULL DEFAULT 0;

-- Update the django_migrations table to mark migration as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('base', '0020_add_menu_permissions', datetime('now'));