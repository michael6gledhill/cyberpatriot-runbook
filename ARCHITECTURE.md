# CyberPatriot Runbook - Application Architecture

## Overview

CyberPatriot Runbook is a desktop GUI application built with PySide6 for managing team security checklists and documentation during CyberPatriot competitions.

## Project Structure

```
cyberpatriot-runbook/
├── app/
│   ├── __init__.py                 # App initialization
│   ├── gui/                        # PySide6 GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py          # Main application window
│   │   ├── login_window.py         # Login and signup UI
│   │   ├── admin_dashboard.py      # Admin dashboard UI
│   │   ├── member_dashboard.py     # Member dashboard UI
│   │   └── dialogs/                # Dialog windows
│   │       └── __init__.py         # Common dialogs
│   ├── controllers/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication & authorization
│   │   └── content.py              # Checklist, README, note operations
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                 # Base model class
│   │   ├── user.py                 # User model
│   │   ├── team.py                 # Team model
│   │   ├── checklist.py            # Checklist models
│   │   ├── readme.py               # README model
│   │   ├── note.py                 # Note model
│   │   └── audit_log.py            # Audit log model
│   ├── database/                   # Database layer
│   │   ├── __init__.py             # DB config & session management
│   │   └── repositories.py         # Data access objects (DAOs)
│   └── security/                   # Security utilities
│       └── __init__.py             # Password & encryption utilities
├── alembic/                        # Database migrations
│   ├── __init__.py
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── resources/                      # Static resources (images, icons)
├── main.py                         # Application entry point
├── config.py                       # Configuration file
├── setup.py                        # Setup script
├── database_setup.sql              # SQL initialization script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # User documentation
├── SETUP.md                        # Setup instructions
└── ARCHITECTURE.md                 # This file
```

## Architecture Layers

### 1. Presentation Layer (GUI)
- **main_window.py**: Stacked widget that manages login and dashboard states
- **login_window.py**: Login and signup UI with PySide6
- **admin_dashboard.py**: Admin dashboard with team, user, and audit management
- **member_dashboard.py**: Member dashboard for checklists, READMEs, and notes
- **dialogs/**: Modal dialogs for user interactions

### 2. Business Logic Layer (Controllers)
- **AuthController**: User registration, login, role management
- **AdminController**: Team CRUD, user approval, role changes
- **ChecklistController**: Checklist progress tracking
- **ReadMeController**: README CRUD operations
- **NoteController**: Note management with encryption

### 3. Data Access Layer (Repositories)
- **UserRepository**: User database operations
- **TeamRepository**: Team database operations
- **ChecklistRepository**: Checklist and progress tracking
- **ReadMeRepository**: README persistence
- **NoteRepository**: Note storage
- **AuditLogRepository**: Activity logging

### 4. Database Layer
- **SQLAlchemy ORM Models**: Defines database schema
- **Alembic Migrations**: Version control for database changes
- **MySQL Database**: Persistent data storage

### 5. Security Layer
- **PasswordManager**: bcrypt password hashing and verification
- **EncryptionManager**: Fernet encryption for sensitive notes

## Data Flow

### User Login Flow
```
LoginWindow.login_button_clicked()
    → AuthController.login()
        → UserRepository.get_user_by_email()
        → PasswordManager.verify_password()
    → MainWindow._on_login_successful()
        → Create AdminDashboard or MemberDashboard
        → AuditLogRepository.log_action()
```

### Checklist Progress Flow
```
MemberDashboard.checklist_selected()
    → ChecklistRepository.get_checklist_by_id()
    → Display items and statuses
    → status_changed()
        → ChecklistRepository.update_checklist_item_status()
        → AuditLogRepository.log_action()
```

### Note Creation with Encryption Flow
```
MemberDashboard._show_create_note_dialog()
    → CreateNoteDialog._handle_create()
    → if encrypt:
        → EncryptionManager.encrypt_note()
        → EncryptionManager.generate_key()
    → NoteRepository.create_note()
    → AuditLogRepository.log_action()
```

## Database Schema

### Key Tables

**users**
- User accounts with role-based access control
- Pending approval flag for new members
- Password stored as bcrypt hash

**teams**
- CyberPatriot teams with ID (NN-NNNN format)
- Division classification

**checklists** & **checklist_items**
- Predefined security checklists
- Individual items for teams to complete

**checklist_status**
- Tracks each user's progress on items
- Stores completion status and notes

**readmes**
- Team knowledge base documents
- Associated with specific OS types
- Visible to all team members

**notes**
- Team notes with encryption support
- Three types: general, point_note, password_change
- Encryption handled with PBKDF2 key derivation

**audit_logs**
- Complete activity history
- Tracks actions by user, resource type, and timestamp

## Security Features

### Authentication
- Email and password login
- bcrypt password hashing (12 rounds)
- Admin direct access, members require approval

### Authorization
- Role-based access control (member, captain, coach, admin)
- Team-scoped data access
- Admin-only operations

### Data Protection
- Sensitive notes encrypted with Fernet (symmetric encryption)
- PBKDF2 key derivation with 100,000 iterations
- Encryption key salt stored separately

### Audit Trail
- All user actions logged
- Timestamp tracking
- Resource change tracking

## Technology Stack

### Frontend
- **PySide6**: Qt-based desktop GUI
- **QMainWindow, QWidget**: Window management
- **QTabWidget**: Tab-based navigation
- **QTableWidget**: Data display

### Backend
- **SQLAlchemy 2.0**: ORM and database abstraction
- **PyMySQL**: MySQL connector
- **bcrypt**: Password hashing
- **cryptography**: Data encryption

### Database
- **MySQL 5.7+**: Primary data storage
- **Alembic**: Schema migration tool

## Design Patterns

### 1. Model-View-Controller (MVC)
- Models: SQLAlchemy ORM classes
- Views: PySide6 GUI components
- Controllers: Business logic classes

### 2. Repository Pattern
- Abstract database access
- Testable data layer
- Easy to swap database backends

### 3. Signal/Slot Pattern (Qt)
- Login window emits signal on successful auth
- Dashboard emits signal on logout
- Decoupled component communication

### 4. Factory Pattern
- MainWindow creates appropriate dashboard based on role
- DatabaseConfig creates engine and sessions

## Deployment

### Local Development
```bash
python main.py
```

### Raspberry Pi
- Install Python 3.9+
- Install MySQL/MariaDB
- Set up systemd service
- Run as daemon

### Containerized (Docker)
- Create Docker image
- Use docker-compose for orchestration
- Mount volumes for persistence

## Future Enhancements

1. **Real-time Collaboration**
   - WebSocket-based live updates
   - Team chat integration

2. **Advanced Reporting**
   - PDF export of checklists
   - Team progress analytics
   - Competition scoring

3. **Mobile Support**
   - Mobile app for checklist viewing
   - Remote notes access

4. **Integration**
   - Slack notifications
   - Email alerts
   - Calendar sync

5. **Performance**
   - Caching layer (Redis)
   - Query optimization
   - Async operations

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### GUI Tests
```bash
pytest tests/gui/ -v
```

## Monitoring and Logging

- Application logs to stdout
- Audit logs stored in database
- Can be extended with file logging
- Can integrate with monitoring tools (ELK stack, Datadog, etc.)

## Conclusion

The CyberPatriot Runbook application follows a clean, layered architecture that separates concerns and makes the codebase maintainable and extensible. The use of PySide6 for GUI and SQLAlchemy for data access provides a robust foundation for a professional desktop application.
