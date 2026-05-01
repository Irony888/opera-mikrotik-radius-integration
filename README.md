# Opera Mikrotik Radius Integration

## Overview
This project integrates Mikrotik routers with a Radius server to provide centralized authentication, authorization, and accounting.

## Features
- Centralized authentication and management for Mikrotik users.
- Support for multiple Radius clients.
- User-friendly interface for configuration and monitoring.
- Real-time accounting and logging of user sessions.

## Requirements
- Mikrotik RouterOS v6.43 or higher.
- A running Radius server (e.g., FreeRADIUS).
- Python 3.7+ for running the backend service.
- PostgreSQL for storing user data and logs.

## Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/Irony888/opera-mikrotik-radius-integration.git
   cd opera-mikrotik-radius-integration
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your Mikrotik router to point to the Radius server.
4. Run the application:
   ```bash
   python app.py
   ```

## API Endpoints
- **POST /api/login**: Authenticate user against Radius server.
- **GET /api/users**: List all users in the system.
- **POST /api/users**: Add a new user.
- **DELETE /api/users/{id}**: Delete a user by ID.

## Architecture
The architecture of the Opera Mikrotik Radius Integration consists of the following components:
- **Frontend**: A web interface built using React.js that communicates with the backend.
- **Backend**: A RESTful API developed in Python Flask that handles requests and interacts with the Radius server and database.
- **Database**: PostgreSQL database storing user information and logs.

---
This documentation should help you set up and understand the Opera Mikrotik Radius Integration project.