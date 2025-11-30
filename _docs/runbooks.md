# ACE Framework: Operational Runbooks

This document provides a collection of one-page runbooks for major operational tasks.

---

## Runbook: Database Migration (SQLite to PostgreSQL)

**Version:** 1.0
**Owner:** Engineering (Infra)
**Last Updated:** 2025-11-30

### 1. Overview

This runbook provides the steps to migrate the ACE framework's database from SQLite to a managed PostgreSQL instance. This is a critical step in improving the scalability and reliability of the system.

### 2. Pre-Migration Checklist

- [ ] A managed PostgreSQL instance has been provisioned.
- [ ] Network access from the Kubernetes cluster to the PostgreSQL instance has been configured and tested.
- [ ] The PostgreSQL credentials have been securely stored in the secret management system.
- [ ] A full backup of the SQLite database has been taken.
- [ ] The application is in a maintenance window, and the API is temporarily disabled.

### 3. Migration Steps

1.  **Export Data from SQLite:**
    -   Use a script to export the data from the `playbook_entries` and `clusters` tables in the SQLite database to a neutral format, such as CSV or JSON.
    -   `python scripts/export_sqlite.py --output-dir /tmp/export`

2.  **Create Schema in PostgreSQL:**
    -   Apply the new database schema to the PostgreSQL instance. This should be done using a schema migration tool like Alembic.
    -   `alembic upgrade head`

3.  **Import Data into PostgreSQL:**
    -   Use a script to import the data from the exported files into the new PostgreSQL tables.
    -   `python scripts/import_postgres.py --input-dir /tmp/export`

4.  **Update Application Configuration:**
    -   Update the application's configuration to point to the new PostgreSQL database. This should be done by updating the relevant Kubernetes Secret and restarting the application deployment.
    -   `kubectl rollout restart deployment/ace-framework`

5.  **Verify the Migration:**
    -   Once the application has restarted, perform a series of checks to ensure that the migration was successful:
        -   Check that the application can connect to the new database.
        -   Run a smoke test to ensure that the API is functioning correctly.
        -   Manually verify that a sample of data from the original SQLite database is present in the new PostgreSQL database.

### 4. Rollback Plan

If the migration fails at any point, follow these steps to roll back to the SQLite database:

1.  **Restore Application Configuration:**
    -   Revert the application configuration to point back to the SQLite database.
    -   `kubectl rollout undo deployment/ace-framework`

2.  **Restore SQLite Database (if necessary):**
    -   If the SQLite database was corrupted during the migration attempt, restore it from the backup that was taken in the pre-migration checklist.

3.  **Investigate and Reschedule:**
    -   Investigate the cause of the failure and reschedule the migration for a future maintenance window.
