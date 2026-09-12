
# Library Management System

A Django-based Library Management System that models real-world library operations — circulation, fines, notifications, role-based access, and a REST API — built with an emphasis on clean architecture and solid business logic.

## Overview

This project goes beyond basic CRUD to implement the actual rules a library needs to run: books can't be borrowed if unavailable, members are capped at 5 active loans, overdue fines accrue daily, and reservations are honored in order. The goal is to demonstrate production-style Django patterns — service layers, custom managers, query optimization, and transactional integrity — on top of a familiar domain.

## Features

### 📚 Member Management
- Register new members
- Edit member profiles
- Activate / deactivate memberships

### 🔄 Borrowing (Circulation)
- Create borrow transactions with enforced business rules:
  - Cannot borrow a book with no available copies
  - Automatically reduces available copy count
  - Stores calculated due date
  - Prevents duplicate active borrows of the same book
  - Enforces a maximum of 5 active books per member

### ↩️ Returning
- Process book returns
- Restore available copy count
- Automatically calculate overdue status

### ⏳ Reservations
- Join a waiting list when a book is unavailable
- First-come, first-served priority queue
- Automatic notification when a reserved book becomes available

### 💰 Fine Management
- Automatic fine calculation for overdue books
- Configurable daily fine rate
- Payment status tracking
- Outstanding balance per member

### 🔔 Notifications
- Due tomorrow reminders
- Overdue alerts
- Reservation availability alerts
- Uses Django's email backend (console backend for local development)

### 📊 Reports
- Active loans
- Overdue books
- Full borrow history
- Most borrowed books

### 🔐 Roles & Permissions
Role-based access control with distinct permission sets for:
- **Administrator** — full system access
- **Librarian** — manage books, loans, and reservations
- **Assistant** — limited operational access
- **Member** — self-service (browse, borrow, view own history)

### 🌐 REST API
Built with Django REST Framework, exposing:
- Books
- Members
- Loans
- Reservations

Includes filtering, pagination, authentication, and permission-scoped access per role.

## Technical Highlights

- **Service layer** — business logic (borrowing, returning, fines, reservations) lives outside views/models for testability and reuse
- **Custom model managers** — encapsulated queries (e.g. `Loan.objects.active()`, `Book.objects.available()`)
- **Query optimization** — `select_related` / `prefetch_related` to avoid N+1 queries in listings and reports
- **Database transactions** — atomic operations for borrow/return/fine flows to guarantee data consistency
- **Signals** *(optional)* — decoupled side effects such as triggering notifications

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django |
| API | Django REST Framework |
| Auth | DRF Authentication & Permissions |
| Email | Django Email Backend (console backend for dev) |
| Database | PostgreSQL / SQLite (dev) |

## Project Structure (suggested)

```
library_system/
├── members/          # Member management
├── circulation/       # Borrowing, returning, reservations
├── fines/             # Fine calculation & payments
├── notifications/     # Email notifications
├── reports/           # Reporting endpoints/queries
├── accounts/           # Roles & permissions
├── api/               # DRF serializers, viewsets, routers
└── core/              # Shared services, managers, utils
```

## Getting Started

```bash
# Clone the repository
git clone https://github.com/<your-username>/library-management-system.git
cd library-management-system

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## API Endpoints (example)

| Endpoint | Description |
|---|---|
| `GET /api/books/` | List books (filterable, paginated) |
| `GET /api/members/` | List members |
| `POST /api/loans/` | Create a borrow transaction |
| `POST /api/loans/{id}/return/` | Return a book |
| `POST /api/reservations/` | Reserve a book |
| `GET /api/reports/overdue/` | Overdue books report |

## Business Rules Summary

- A member may hold **at most 5** active loans at once
- A book **cannot** be borrowed if no copies are available
- A member **cannot** borrow the same book twice while a loan is active
- Fines accrue **daily** once a loan passes its due date
- Reservations are served in **first-in, first-out** order

## Roadmap / Possible Extensions

- [ ] Renewal requests (extend due date)
- [ ] SMS notifications
- [ ] Book recommendations
- [ ] Multi-branch library support
- [ ] Admin dashboard analytics

## License

MIT License — feel free to use this project as a learning reference or starting point.
