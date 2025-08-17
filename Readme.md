# Multi-Tenant Resource Management System (FastAPI + PostgreSQL + Schema-per-Tenant)

## APP FEATURES:
- **Schema-per-tenant** implemented using PostgreSQL `search_path` switching per request.
- **Super Admin** manages tenants in the **public** schema.
- **JWT Auth** with tenant awareness (claims include `tenant_id`, `role`, `uid`).
- **RBAC**: `ADMIN`, `MANAGER`, `EMPLOYEE` enforced via dependencies.
- **Soft deletes** for `users` and `resources`.
- **Business limits**: max 50 users/tenant, 500 resources/tenant, 10 resources per user.
- **Audit logs** for all create/update/delete actions.
- **Search & pagination** for resources.
- **Indexes** for performance (`resources.name`, `resources.owner_id`, `audit_logs.timestamp`).

## Steps for Running locally
1. Create a Postgres DB and set `DATABASE_URL` in `.env` (see `app/config.py` for default):
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/multitenant
   JWT_SECRET=change-this-secret
   SUPERADMIN_USERNAME=superadmin
   SUPERADMIN_PASSWORD=supersecret
   ```
2. Install deps and start server:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## API Usage
### 1) Login as Super Admin
```
POST /auth/login
Headers: X-Tenant-ID: SUPER
Body: { "username": "superadmin", "password": "supersecret" }
```
Response: `access_token` (role = `SUPERADMIN`).

### 2) Create a Tenant (Super Admin only)
```
POST /tenants
Authorization: Bearer <SUPERADMIN token>
Body: { "name": "Tenant1 Corp", "schema_name": "tenant1" }
```
- Creates schema `tenant1` and initializes tables.

### 3) Bootstrap tenant admin user
- Temporarily **switch header to tenant schema** and create first admin by direct SQL insert. For simplicity, run in psql:
  ```sql
  set search_path to tenant1, public;
  insert into users (username, password_hash, role, is_deleted) values ('tenant1_aamin', '$2b$12$jE5lLpL1gsKIwAa.Pk5O0.GlysQOzuyojakqYI2MlIPs5Xk/X9Amy', 'ADMIN', false);
  ```
  (We can generate a bcrypt hash using any tool; or add a one-time internal script.)

### 4) Tenant user login
```
POST /auth/login
Headers: X-Tenant-ID: tenant1
Body: { "username": "tenant1_aamin", "password": "tenant1admin@123" }
```

### 5) Tenant APIs (use the tenant token + header `X-Tenant-ID: tenant1`)
- **Users (Admin):**
  - POST /users
  - DELETE /users/{id}
- **Resources (Admin/Manager):**
  - POST /resources
  - PUT /resources/{id}
  - DELETE /resources/{id}
- **Resources (Employee/Admin/Manager):**
  - GET /resources?name=foo&owner_id=1&page=1&size=20
  - GET /resources/{id}
- **Audit (Admin):**
  - GET /audit-logs

## Notes
- Tenant isolation is guaranteed by per-request `search_path` switching and absence of cross-tenant identifiers in queries.
- All soft-deleted rows are excluded using explicit filters in queries.
- Business limits are enforced in the CRUD service layer.
- To remove a tenant: `DELETE /tenants/{id}` (Super Admin token required).
