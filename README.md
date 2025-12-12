# KanMind

KanMind is a lightweight Kanban-style ticket manager built with Django and Django REST Framework. It provides boards, tasks, and comments APIs with token-based authentication.

## Features

- Boards with owners and members
- Tasks with status, priority, assignee, reviewer, and due dates
- Comments on tasks
- Token-based authentication (register/login) with standardized responses
- Permission model enforcing owner/member access rules

## Requirements

- Python 3.13 (project uses a local `env` virtual environment)
- Django 5.x
- Django REST Framework 3.16.x

Dependencies are pinned in `requirements.txt`.

## Quick Start

1. Create and activate a virtual environment (if not using the provided `env/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Run the development server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Using the Provided `env/` (optional)

This repository includes an `env/` folder with a pre-initialized virtual environment for macOS. You can activate it directly:

```bash
source env/bin/activate
```

If you prefer your own environment, ignore the `env/` folder and follow Quick Start.

## Project Structure

- `core/`: Django project settings and entry points
- `auth_app/`: Authentication app (models, serializers, views)
- `kanban_app/`: Kanban domain app (models, serializers, views, permissions)
- `db.sqlite3`: Default SQLite database for local development

## Authentication

KanMind uses DRF Token Authentication. Obtain a token via registration or login, then include it in requests:

```
Authorization: Token <your_token>
```

### Endpoints

- Register: `POST /auth/register/`

  - Body: `{ "email": "...", "password": "...", "repeated_password": "...", "fullname": "..." }`
  - Response: `{ token, user_id, email, fullname }`

- Login: `POST /auth/login/`

  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ token, user_id, email, fullname }`

- Accounts list (admin/informational): `GET /auth/accounts/`

Note: Actual auth URL prefixes depend on your `core/urls.py` configuration.

## Kanban API

Router-based endpoints (via `kanban_app/api/urls.py`) and named paths:

- Boards (router):

  - `GET /api/boards/` — List boards where you are owner or member
  - `POST /api/boards/` — Create a board (owner set to requester)
  - `GET /api/boards/{id}/` — Retrieve board details (members, tasks)
  - `PATCH /api/boards/{id}/` — Update title/members
  - `DELETE /api/boards/{id}/` — Delete board (owner only)

- Tasks (router):

  - `POST /api/tasks/` — Create task (board access required)
  - `GET /api/tasks/{id}/` — Retrieve task
  - `PATCH /api/tasks/{id}/` — Update task (cannot change its board)
  - `DELETE /api/tasks/{id}/` — Delete task (task creator or board owner)

- Task filters:

  - `GET /api/tasks/assigned-to-me/` — Tasks where you are assignee
  - `GET /api/tasks/reviewing/` — Tasks where you are reviewer

- Task comments:
  - `GET /api/tasks/{task_id}/comments/` — List comments for task
  - `POST /api/tasks/{task_id}/comments/` — Create comment for task
  - `DELETE /api/tasks/{task_id}/comments/{pk}/` — Delete a comment (author only)

### Permissions Overview

- Board access: owner or member
- Task access: owner or member of the task’s board
- Task deletion: task creator or the board owner
- Comment deletion: comment author only

## Data Model Summary

- `Board(title, owner, members)`
- `Task(title, description?, status, priority, board, created_by, assignee?, reviewer?, due_date?)`
- `Comment(author, content, created_at, task)`

Statuses: `to-do`, `in-progress`, `review`, `done`

Priorities: `low`, `medium`, `high`

## Running Tests (optional)

If you add tests, run them with:

```bash
python manage.py test
```

## Development Tips & Special Notes

- Board changes are blocked on task updates (you cannot move a task to another board via update).
- `assignee_id` and `reviewer_id` must be board members when creating/updating tasks.
- Use token auth for all Kanban API requests; unauthenticated requests are rejected.
- The default DB is SQLite for convenience; switch to PostgreSQL/MySQL in production.

## License

This project is proprietary to the repository owner. No license file is included.
