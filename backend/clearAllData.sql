-- =============================================================================
--                  Clear All Data Script
--
-- WARNING: This is a destructive operation. It will permanently delete
--          all data from all tables in the database. There is no undo.
--
-- This script is useful for resetting your development database to a clean slate
-- without having to drop and recreate the entire structure.
--
-- To run this file from your terminal:
-- psql -d your_database_name -f clear_data.sql
--
-- =============================================================================

-- The TRUNCATE command is used to quickly remove all rows from a set of tables.
--
-- We list all tables that hold data.
--
-- RESTART IDENTITY is good practice to reset any underlying sequences, although
-- we are using UUIDs as primary keys.
--
-- CASCADE is the most important part. It automatically truncates all tables
-- that have foreign-key references to the listed tables. For example, because
-- 'wells' is listed, CASCADE ensures that 'well_projects' and 'breakage_reports'
-- are also truncated, respecting the dependency order.

TRUNCATE
    areas,
    admins,
    wells,
    well_projects,
    breakage_reports
RESTART IDENTITY CASCADE;

-- Confirmation message
SELECT 'Successfully cleared all data from all tables.' as status;

-- =============================================================================
--                             End of Script
-- =============================================================================
