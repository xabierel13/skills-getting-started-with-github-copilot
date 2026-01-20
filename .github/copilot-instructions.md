# AI Coding Agent Instructions

## Project Overview
This is a **Mergington High School Activities API** – a lightweight FastAPI application for managing student extracurricular activities. It's a full-stack project with a Python backend and vanilla JavaScript frontend.

**Core purpose:** Students can browse activities and sign up using their school email.

## Architecture & Key Components

### Backend: FastAPI Server (`src/app.py`)
- **Language:** Python 3, FastAPI framework
- **Data storage:** In-memory dictionary (resets on server restart) – activities stored by name as key
- **Entry point:** Run with `python src/app.py` (uses Uvicorn default: http://localhost:8000)
- **API endpoints:**
  - `GET /activities` – Returns full activities dict with descriptions, schedule, max_participants, and participants list
  - `POST /activities/{activity_name}/signup?email=student@mergington.edu` – Adds email to activity's participants list
  - `GET /` – Redirects to static frontend at `/static/index.html`

### Frontend: Static HTML/JS (`src/static/`)
- **index.html:** Two-section layout (activities display + signup form)
- **app.js:** Fetches `/activities` endpoint on page load, renders cards, handles form submission
- **styles.css:** Responsive design (not detailed in this doc, see file for styling patterns)
- **No frameworks:** Vanilla JS with DOM manipulation – all logic is imperative

## Data Flow
1. Page loads → `fetchActivities()` fetches from `/activities` endpoint
2. JS renders activity cards showing `max_participants - len(participants)` as "spots left"
3. User submits form with email + selected activity name
4. JS sends POST to `/activities/{activity_name}/signup?email={email}`
5. Backend appends email to activity's participants list
6. Response shows success/error message

## Critical Workflows

### Running the App
```bash
pip install -r requirements.txt
python src/app.py
```
Then open browser to http://localhost:8000 (auto-redirects to `/static/index.html`).

### Testing
```bash
pytest
```
Note: `pytest.ini` sets pythonpath to `.` for imports from root level.

## Important Patterns & Conventions

### Validation Gaps (Known Issues)
- **No duplicate signup prevention:** Same email can sign up multiple times for same activity
- **No capacity enforcement:** POST doesn't check if max_participants is exceeded before adding
- **Missing error handling:** Backend doesn't validate activity exists in signup OR validate email format
- **No data persistence:** In-memory dict means all changes lost on server restart

These are intentional design simplifications for a learning project but are good targets for improvement tasks.

### Data Model Quirks
- Activities identified by **exact name string** (e.g., "Chess Club") – substring matching will fail
- Email stored as-is, no normalization (case-sensitive)
- No Student model/table – just email strings in participants list
- Frontend assumes activities dict key order is deterministic (JavaScript objects maintain insertion order in modern browsers)

### Frontend Conventions
- **Event listeners:** All bound in `DOMContentLoaded` to ensure DOM is ready
- **Error handling:** Fetch errors show generic message, logs to console
- **Message display:** Success/error messages fade after 5 seconds via `hidden` class
- **Form reset:** Cleared on successful signup
- **URL encoding:** Uses `encodeURIComponent()` for activity name (handles spaces correctly)

## Integration Points
- Frontend talks to backend only via fetch to `/activities` and `/activities/{activity_name}/signup`
- No authentication/authorization layer
- No CORS setup needed (same origin)
- Static files served by FastAPI's `StaticFiles` mounting at `/static`

## File Reference
| File | Purpose |
|------|---------|
| `src/app.py` | Core API logic |
| `src/static/index.html` | Page structure |
| `src/static/app.js` | Client-side logic & API calls |
| `src/static/styles.css` | Styling |
| `requirements.txt` | Python dependencies (fastapi, uvicorn) |
| `pytest.ini` | Test configuration |

## Common Extension Points
- **Add validation:** Modify POST handler to check capacity & duplicates
- **Add persistence:** Replace dict with file-based JSON or SQLite database
- **Add features:** Student profiles, activity ratings, waitlists, admin endpoints
- **Improve frontend:** Add loading states, activity search/filtering, client-side validation
