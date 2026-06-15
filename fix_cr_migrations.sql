-- SQL script to add missing columns to contec_cr_changerequest table
-- Run this in your database to fix the migration issue

ALTER TABLE contec_cr_changerequest 
ADD COLUMN department VARCHAR(100) NULL;

ALTER TABLE contec_cr_changerequest 
ADD COLUMN job_name VARCHAR(100) NULL;

ALTER TABLE contec_cr_changerequest 
ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';

-- Update the django_migrations table to mark migrations as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('contec_cr', '0003_add_department_job_name', datetime('now'));

INSERT INTO django_migrations (app, name, applied) 
VALUES ('contec_cr', '0004_add_priority_field', datetime('now'));