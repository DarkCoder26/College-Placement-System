# College Placement Analysis System

A beginner-friendly Flask web application for student placement CRUD, search/filtering, Pandas-based analytics, and CSV reports. Uses Python 3, SQLite, SQL, HTML5, CSS3, Jinja2, Flask-WTF CSRF protection, and pytest.

> **Educational use:** This project does not include authentication or role-based access. Do not expose it publicly or use real sensitive student data without adding appropriate security controls.

## Features
- Dashboard metrics calculated from live SQLite records.
- Student create, view, update, and delete.
- Search by name/roll number; department/status/year filters; sorting and pagination.
- Department, company, and graduation-year placement analytics using Pandas.
- Student and analytics CSV downloads with UTF-8 BOM for spreadsheet compatibility.
- Server-side validation, database constraints, parameterized SQL, CSRF tokens, responsive pages.
- Automated tests using a temporary isolated SQLite database.

## Requirements
Python 3.10 or newer, VS Code (recommended), and a modern browser. Install dependencies from `requirements.txt`.

## Windows setup (PowerShell)
1. Extract the ZIP file and open the `CollegePlacementSystem` folder in VS Code.
2. Open **Terminal → New Terminal**. Ensure the terminal is in the folder containing `app.py`.
3. Create a virtual environment:
   ```powershell
   py -3 -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt instead: `.venv\Scripts\activate.bat`. You may also run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current PowerShell window if permitted by your organisation.
5. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. (Optional) load fictional demonstration records once:
   ```powershell
   python seed_data.py
   ```
   If the database already contains any student rows, the script intentionally skips seeding to avoid duplicates. To start empty, skip this command. The database is created automatically at `instance\placement.db`.
7. Start the app:
   ```powershell
   python app.py
   ```
8. Open **http://127.0.0.1:5000** in Chrome, Edge, or Firefox. Keep the terminal open while using the app. Press `Ctrl+C` to stop it.

### Environment configuration
A development-only fallback secret is provided for convenient local demonstration. Before any deployment, set a strong random `FLASK_SECRET_KEY` and `PLACEMENT_DATABASE` as appropriate. In PowerShell for the current terminal:
```powershell
$env:FLASK_SECRET_KEY = "replace-with-a-long-random-secret"
$env:PLACEMENT_DATABASE = "$PWD\instance\placement.db"
$env:FLASK_DEBUG = "0"
python app.py
```
Debug mode is off by default. Only use `FLASK_DEBUG=1` on a local development machine.

## Verify the sample data
The included seed command adds 12 fictional students across three departments and two graduation years. Expected figures:
- Total students: 12
- Placed: 8
- Not placed: 4
- Placement rate: 8 / 12 × 100 = **66.7%**
- Average package for placed students: **6.375 LPA** (shown rounded to 6.38 LPA)
- Highest package: **9.50 LPA**
- Departments: 3

These are sample-data calculations only, not actual college outcomes.

## CSV reports
- Student records: Dashboard → Students → Export CSV, or `/reports/students.csv`.
- Analytics: Analytics → Export analytics CSV, or `/reports/analytics.csv`.
Files are generated from the current database when requested.

## Tests
Install dependencies, then run:
```powershell
python -m pytest -v
```
The test fixture creates a temporary database for each test and does not overwrite `instance\placement.db`. Tests disable CSRF only within the test configuration; the real application retains CSRF protection.

## Troubleshooting
- **`py` not found:** Install Python from the official Python website and tick “Add Python to PATH”; reopen the terminal.
- **Activation is disabled:** Use Command Prompt activation or the PowerShell process-scoped policy command shown above.
- **`ModuleNotFoundError`:** Activate `.venv`, then run `python -m pip install -r requirements.txt`.
- **Port 5000 in use:** Run `$env:PORT="5001"; python app.py`, then visit `http://127.0.0.1:5001`.
- **CSRF token missing:** Use the application forms in the browser and do not remove the hidden `csrf_token` field. Refresh after a stale page.
- **Pandas install error:** Confirm Python is 3.10+ and update pip before installing.
- **Sample seed did not add rows:** This is intentional when the database already has one or more records; the script will not add duplicates.

## Project files
- `app.py`: routes, request handling, validation, configuration.
- `database.py`: SQLite schema, connection management, SQL CRUD, dashboard metrics.
- `analysis.py`: Pandas calculations and CSV creation.
- `seed_data.py`: optional idempotent sample-data loader.
- `templates/`: Jinja2 pages.
- `static/`: CSS and JavaScript.
- `tests/test_app.py`: automated route and calculation tests.
- `PROJECT_REPORT.md`: college project report, diagrams, workflow, and viva preparation.
