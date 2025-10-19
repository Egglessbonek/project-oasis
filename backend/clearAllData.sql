-- Clear all data from tables in the correct order to respect foreign key constraints
TRUNCATE TABLE breakage_reports CASCADE;
TRUNCATE TABLE well_projects CASCADE;
TRUNCATE TABLE wells CASCADE;
TRUNCATE TABLE admins CASCADE;
TRUNCATE TABLE areas CASCADE;