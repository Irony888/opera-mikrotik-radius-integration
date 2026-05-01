# System Architecture

## Overview

The Opera PMS - MikroTik - FreeRADIUS Integration system is designed to provide seamless WiFi authentication for hotel guests and staff by integrating three key components.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Hotel Network                            │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐   │
│  │  Opera PMS      │  │  Guest Portal   │  │  WiFi AP    │   │
│  │  (Guest Data)   │  │  (Login UI)     │  │  (MikroTik) │   │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘   │
│           │                    │                  │           │
│           └────────────────────┼──────────────────┘           │
│                                │                              │
│                      ┌─────────▼─────────┐                   │
│                      │ Integration       │                   │
│                      │ Service (Python)  │                   │
│                      └────────┬──────────┘                   │
│                               │                              │
│        ┌──────────────────────┼──────────────────────┐      │
│        │                      │                      │      │
│        ▼                      ▼                      ▼      │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────┐ │
│  │ PostgreSQL   │    │  FreeRADIUS      │    │ MikroTik │ │
│  │ Database     │    │  Auth Server     │    │ Router   │ │
│  └──────────────┘    └──────────────────┘    └──────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. Opera Connector (`opera_connector.py`)
Handles communication with Opera PMS API to fetch guest and staff information.

**Responsibilities:**
- Authenticate with Opera PMS API
- Fetch guest check-in/check-out data
- Retrieve staff information
- Poll for real-time updates
- Handle API rate limiting and retries

**Key Methods:**
```python
- get_guests() -> List[Guest]
- get_guest(guest_id) -> Guest
- get_staff() -> List[Staff]
- sync_users() -> SyncResult
```

### 2. MikroTik Connector (`mikrotik_connector.py`)
Manages interaction with MikroTik routers for network access control.

**Responsibilities:**
- Connect to MikroTik RouterOS API
- Create/update/delete user profiles
- Configure bandwidth limits
- Manage firewall rules
- Monitor connection status

**Key Methods:**
```python
- add_user(username, password) -> bool
- update_user_bandwidth(username, limits) -> bool
- remove_user(username) -> bool
- get_online_users() -> List[User]
```

### 3. FreeRADIUS Manager (`radius_manager.py`)
Manages FreeRADIUS server for centralized authentication.

**Responsibilities:**
- Manage user credentials in RADIUS database
- Create/update/delete RADIUS user accounts
- Assign user groups and profiles
- Manage session attributes
- Handle authentication logging

**Key Methods:**
```python
- add_radius_user(username, password, profile) -> bool
- update_radius_user(username, attributes) -> bool
- remove_radius_user(username) -> bool
- get_user_sessions(username) -> List[Session]
```

### 4. Authentication Handler (`auth_handler.py`)
Orchestrates the entire authentication workflow.

**Responsibilities:**
- Synchronize users from Opera PMS
- Provision users in FreeRADIUS and MikroTik
- Deactivate users on checkout
- Manage user lifecycle
- Handle concurrent session management

**Workflow:**
```
Opera PMS Guest Data
    ↓
Fetch from Opera API
    ↓
Check against Database
    ↓
Provision in FreeRADIUS ──→ Set credentials
    ↓
Update in MikroTik ─────→ Set bandwidth/policies
    ↓
Store in Database
    ↓
Return to Guest Portal
```

### 5. Database Module (`database.py`)
Manages persistent storage and caching.

**Stored Data:**
- User information (guests and staff)
- Authentication history
- Connection logs
- Bandwidth usage statistics
- System events and errors

**Schema:**
- `users` - User accounts and credentials
- `sessions` - Active user sessions
- `logs` - Authentication and connection logs
- `bandwidth_usage` - Per-user usage statistics
- `devices` - Connected devices
- `events` - System events and audit trail

## Data Flow

### Guest Check-in Process
```
1. Guest checks in at Opera PMS reception
   ↓
2. Opera PMS records check-in
   ↓
3. Integration service polls Opera API (every 5 mins)
   ↓
4. Detects new guest
   ↓
5. Creates RADIUS account with temporary password
   ↓
6. Configures MikroTik bandwidth limits
   ↓
7. Stores guest info in local database
   ↓
8. Guest receives WiFi credentials (SMS/email/portal)
   ↓
9. Guest connects to WiFi and authenticates via RADIUS
```

### Guest Check-out Process
```
1. Guest checks out at Opera PMS
   ↓
2. Opera PMS records check-out
   ↓
3. Integration service detects check-out
   ↓
4. Terminates active sessions in MikroTik
   ↓
5. Deactivates RADIUS account
   ↓
6. Logs usage statistics
   ↓
7. Updates database status to "checked_out"
   ↓
8. Guest access is immediately revoked
```

## Security Considerations

### 1. Credential Management
- Passwords stored encrypted in database
- RADIUS shared secret in environment variables
- API credentials in secure vault
- Regular password rotation for staff

### 2. Network Security
- SSL/TLS for all API communications
- Firewall rules to restrict RADIUS access
- SSH for MikroTik connections
- VPN for remote access

### 3. Data Protection
- Database encryption at rest
- Secure logs with access control
- PII anonymization in audit trails
- GDPR compliance for guest data

### 4. Access Control
- Role-based access control (RBAC)
- API authentication via API keys
- Session management with timeout
- Activity logging and monitoring

## Performance Considerations

### Caching
- Cache guest list in memory (5-min TTL)
- Cache staff information (hourly update)
- Connection pool for database
- RADIUS client connection pooling

### Scalability
- Horizontal scaling via load balancer
- Database read replicas
- RADIUS server clustering
- Queue-based async processing for bulk operations

### Monitoring
- Health checks on all services
- Prometheus metrics exposure
- Log aggregation
- Alert thresholds for anomalies

## Error Handling

All components implement retry logic:
- Exponential backoff for API calls
- Circuit breaker for failed services
- Graceful degradation
- Comprehensive error logging

## Configuration

See `config/config.example.yaml` for all configurable parameters.

## Deployment

See `docs/INSTALLATION.md` for deployment instructions.
