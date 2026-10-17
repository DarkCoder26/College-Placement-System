# College Placement Analysis System — BCA Project Report

> Replace all bracketed fields with your own details. This document is a report template; the certificate is not an official approval.

## 1. Title Page
**Project:** College Placement Analysis System  
**Submitted by:** [Student Name]  
**Roll Number:** [Roll Number]  
**Programme:** Bachelor of Computer Applications (BCA)  
**College:** [College Name]  
**University:** [University Name]  
**Project Supervisor:** [Supervisor Name]  
**Submission Date:** [DD Month YYYY]

## 2. Certificate Template
This is to certify that the project titled “College Placement Analysis System” has been prepared by [Student Name], Roll Number [Roll Number], as part of the academic requirements for [Programme/University]. The work and its evaluation are subject to the institution's review and approval.

Supervisor: [Name and Signature]  
Head of Department: [Name and Signature]  
Date: [Date]  
*Use only after review and signature by the authorised institution. This template is not proof of approval.*

## 3. Declaration Template
I, [Student Name], declare that this project report titled “College Placement Analysis System” is submitted by me for academic evaluation. Any third-party material used has been acknowledged in the references. I understand that the institution may verify the work.

Signature: [Student Name] · Date: [Date]

## 4. Acknowledgement
I thank [Supervisor Name], the faculty of [Department/College], and my family and peers for their guidance and support during the development of this academic project.

## 5. Abstract
The College Placement Analysis System is a local web application that centralises student placement records and provides placement summaries. The application is implemented using Python and Flask, stores structured records in SQLite, uses SQL for database operations, and uses Pandas to analyse placement outcomes. Users can create, read, update, and delete student records; search and filter records; review department-, company-, and graduation-year summaries; and download CSV reports. Server-side validation, database constraints, parameterized SQL, and CSRF protection improve data integrity and request safety. The system is designed for demonstration and learning, and does not include production-grade authentication.

## 6. Table of Contents
1. Introduction  2. Problem Statement  3. Objectives  4. Scope  5. Existing and Proposed Systems  6. Requirements and Feasibility  7. Architecture and DFD  8. Use Cases  9. Database Design  10. Modules  11. Algorithms  12. Implementation  13. Testing  14. Results  15. Limitations and Future Scope  16. Conclusion  17. References  18. Viva Questions

## 7. Introduction
Campus placement information is useful to students, placement officers, and administrators. If records are maintained across separate spreadsheets, duplicate entries and inconsistent calculations can occur. This project provides a single local interface for maintaining placement records and computing summaries from saved data.

## 8. Problem Statement
Manual record maintenance makes it harder to find individual records, compare departments, and consistently calculate placement percentages and package statistics. A small database-backed application can improve organisation and reduce repetitive calculations.

## 9. Objectives
- Maintain a structured record for each student.
- Enforce unique roll numbers and valid CGPA/package values.
- Provide CRUD, search, filters, sorting, and pagination.
- Calculate overall and grouped placement statistics.
- Export current records and analytics as CSV.
- Demonstrate a full-stack Python application with a relational database.

## 10. Scope
The project supports local administration of student placement data for a demonstration or small educational use case. It covers records, analysis, and CSV exports. It does not manage job applications, interviews, user accounts, offers requiring multiple companies per student, or live integrations with college ERP systems.

## 11. Existing and Proposed Systems
**Existing approach:** spreadsheets or manually maintained registers. They can be easy to start with but require manual validation, filtering, and calculations.  
**Proposed approach:** Flask pages use validated forms and parameterized SQL to store data in SQLite. Pandas aggregates stored records for analysis, and reports are generated on demand.

## 12. Hardware and Software Requirements
- Hardware: typical laptop/desktop, 4 GB RAM recommended, modest free disk space.
- OS: Windows 10/11.
- Python: 3.10+.
- Editor: Visual Studio Code (recommended).
- Browser: Chrome, Edge, or Firefox.
- Libraries: Flask, Flask-WTF, Pandas, pytest.
- Database: SQLite (included with Python).

## 13. Feasibility Study
- **Technical:** uses widely available Python packages and an embedded SQLite database.
- **Economic:** no paid service or database server is required.
- **Operational:** form-based pages and a dashboard are suitable for a small local demonstration.
- **Schedule:** the modular design allows implementation and testing in manageable steps.

## 14. System Architecture
Browser (HTML/CSS/JavaScript) → Flask routes and validation → database access functions → SQLite database. The analytics module loads database records into a Pandas DataFrame, calculates summaries, and returns values to Jinja templates or CSV generation. CSRF protection applies to form submissions.

### Data Flow Diagram (Level 0)
```text
[Administrator/User]
        | student data, filters
        v
[College Placement Analysis System]
        | SQL read/write            | analytics/report request
        v                           v
   [SQLite Database]          [Pandas Analysis]
        |                           |
        +------ records/results ----+
                    |
                    v
             [Dashboard / CSV]
```

### Data Flow Diagram (Level 1)
```text
User -> 1. Validate Form -> 2. Student CRUD Module -> SQLite
User -> 3. Search/Filter -> SQLite -> Student List
SQLite -> 4. Analytics Module (Pandas) -> Dashboard Charts/Tables
SQLite -> 5. Report Module -> CSV download -> User
```

## 15. Use-Case Description
**Actor:** local administrator/user.  
**Use cases:** view dashboard; add student; browse/search/filter students; edit student; delete student after confirmation; view analytics; export student CSV; export analytics CSV.  
**Precondition:** application is running locally.  
**Main flow:** user opens a page, submits a form or filter, server validates the input, SQL accesses the database, and the result is rendered or downloaded.  
**Alternate flow:** invalid form data produces a validation message; unknown routes or records show a 404 page.

## 16. Database Schema and ER Diagram
The project uses one table, `students`, because the current requirements do not need separate company or department entities.

| Column | Type | Rules |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| roll_number | TEXT | Required, unique, max 30 chars |
| full_name | TEXT | Required, max 100 chars |
| department | TEXT | Required, max 80 chars |
| graduation_year | INTEGER | 2000–2100 |
| cgpa | REAL | 0–10 |
| placement_status | TEXT | Placed or Not Placed |
| company_name | TEXT | Required only for placed records |
| job_role | TEXT | Required only for placed records |
| package_lpa | REAL | Non-negative; >0 if placed, 0 otherwise |
| created_at | TEXT | SQLite timestamp |

```text
+----------------------------+
|          STUDENTS          |
+----------------------------+
| PK id                      |
| UQ roll_number             |
|    full_name               |
|    department              |
|    graduation_year         |
|    cgpa                    |
|    placement_status        |
|    company_name            |
|    job_role                |
|    package_lpa             |
|    created_at              |
+----------------------------+
```

## 17. Module Descriptions
- **Dashboard:** live totals, placement rate, average/highest package, department count, recent students.
- **Student management:** validated create/edit forms, list view, and confirmed deletion.
- **Search and filtering:** name/roll search, department/status/year filters, sort controls, and pagination.
- **Analytics:** Pandas DataFrame aggregation by department, company, and graduation year.
- **Reports:** CSV exports of current records and grouped summaries.
- **Database layer:** schema creation, constraints, parameterized queries, and transaction commits.
- **Testing:** isolated temporary database tests for routes and calculation logic.

## 18. Algorithms and Formulas
Let `N` be all students and `P` be placed students:
- Not placed = `N − P`.
- Overall placement percentage = `P / N × 100`; if `N = 0`, return 0%.
- Average package = sum of placed-student packages / `P`; if `P = 0`, return 0.
- Highest package = maximum placed-student package; if `P = 0`, return 0.
- Department placement percentage = department placed count / department total × 100; if department total is 0, return 0.
- Company recruitment count = number of placed records for that company.
Intermediate values are not rounded; display values are formatted for readability.

## 19. Implementation Details
Flask maps URLs to Python functions. Jinja2 renders templates using values passed by the route. SQLite stores records in `instance/placement.db`. SQL uses placeholders for user-supplied values. Pandas performs grouped analysis and CSV conversion. CSS provides responsive layout; JavaScript supports a mobile navigation toggle, placement-field UI, and delete confirmation. CSRF tokens are included in forms through Flask-WTF.

## 20. Testing Strategy and Results
Automated tests are in `tests/test_app.py`. They cover startup and empty state, adding valid records, duplicate roll numbers, invalid CGPA, negative packages, search/filter, update/delete, calculations, CSV export, analytics/about routes, and unknown URLs. Each fixture uses a temporary SQLite database.

**Actual result status:** the generated bundle includes the tests, but the tests must be executed in the target environment using `python -m pytest -v`. Do not claim tests passed unless you have run them and recorded the output. Record your run here:
- Date/environment: [Fill in]
- Command: `python -m pytest -v`
- Result: [Paste actual passed/failed count and investigate any failures]

## 21. Screenshots to Capture
1. Dashboard with sample records.
2. Student list and filters.
3. Add student form.
4. Validation message for duplicate roll number.
5. Edit student page.
6. Analytics page with department comparison.
7. CSV opened in a spreadsheet application.
8. About page.

## 22. Results and Discussion
When run with the optional fictional sample dataset, the dashboard should show 12 students, 8 placed, 4 not placed, 66.7% placement rate, average package 6.38 LPA, highest package 9.50 LPA, and 3 departments. These values validate the formulas against a known demonstration dataset and are not real college statistics.

## 23. Limitations
No login/authentication, no multi-user roles, no import workflow, no audit trail, no backup scheduler, and no integration with a college ERP. One student record holds one placement outcome. The local development setup is not production hardened.

## 24. Future Scope
Add authentication and role-based access, audit logs, import from validated CSV/Excel, PDF/Excel reports, multiple offers per student, placement-drive management, backups, and secure deployment.

## 25. Conclusion
The College Placement Analysis System demonstrates how a small web application can combine Flask, SQLite, SQL, and Pandas to maintain records and produce repeatable placement statistics. Its modular structure and tests make it appropriate for a BCA project demonstration, while its documented security limitations identify the work needed before real-world deployment.

## 26. References
- Python documentation: https://docs.python.org/3/
- Flask documentation: https://flask.palletsprojects.com/
- Flask-WTF documentation: https://flask-wtf.readthedocs.io/
- SQLite documentation: https://www.sqlite.org/docs.html
- Pandas documentation: https://pandas.pydata.org/docs/
- pytest documentation: https://docs.pytest.org/

## 27. Viva Questions and Answers
1. **What is Python?** A high-level programming language used for application logic and data processing.
2. **What is Flask?** A lightweight Python web framework that maps HTTP requests to view functions.
3. **What is a route?** A URL rule connected to a Python function.
4. **What is Jinja2?** A template engine used to render dynamic HTML.
5. **What is HTML?** The markup language that structures web pages.
6. **What is CSS?** A language used to style and lay out HTML.
7. **What is SQLite?** A serverless, file-based relational database engine.
8. **What is SQL?** A language for querying and modifying relational data.
9. **What is a primary key?** A column or set of columns that uniquely identifies a row.
10. **What is a unique constraint?** A database rule that prevents duplicate values in a column or combination.
11. **What is CRUD?** Create, Read, Update, and Delete.
12. **Why use parameterized queries?** They separate data from SQL syntax and help prevent SQL injection.
13. **What is SQL injection?** An attack where crafted input changes the meaning of a SQL statement.
14. **What is Pandas?** A Python library for tabular data analysis and manipulation.
15. **What is a DataFrame?** A two-dimensional labelled data structure in Pandas.
16. **Why use Pandas in this project?** To aggregate and summarise placement data by department, company, and year.
17. **What is CSV?** Comma-separated values, a plain-text tabular data format.
18. **How is placement percentage calculated?** Placed students divided by all students, multiplied by 100.
19. **Why exclude unplaced students from average package?** They have no placement package, so including zeros would understate the average offer package.
20. **How are empty datasets handled?** Counts and rates safely return zero and tables show empty states.
21. **What is CSRF?** Cross-Site Request Forgery, where a browser is tricked into submitting an unwanted authenticated request.
22. **How is CSRF protection enabled?** Flask-WTF's CSRFProtect checks a token on state-changing form submissions.
23. **What is server-side validation?** Checking submitted values on the server rather than trusting browser controls.
24. **What is pagination?** Dividing a large list into smaller pages.
25. **What is an index in a database?** A structure that can speed up searches on selected columns.
26. **Why is roll number unique?** It acts as a student identifier and prevents duplicate records.
27. **What is the Post/Redirect/Get pattern?** After a successful POST, redirect to a GET page to reduce accidental resubmission.
28. **What is a unit test?** A repeatable test of a function or application behaviour.
29. **Why use a separate test database?** To keep test changes isolated from actual project data.
30. **What is the main limitation of this version?** It has no authentication/authorisation and is intended for local educational use.
31. **How does the dashboard get its data?** It runs aggregate SQL queries against the current SQLite database.
32. **What happens when a student is Not Placed?** Company and job role are stored as blank and package is stored as zero.
33. **Why is a transaction/commit needed?** To persist a group of database changes and define a transaction boundary.
34. **What is the purpose of `requirements.txt`?** It lists packages needed to set up the Python environment.
35. **Explain the application workflow.** The user opens a page in a browser; Flask receives the request, validates input if submitted, uses parameterized SQL to read/write SQLite, and renders a Jinja template. For analytics, Pandas groups current database rows and the app displays summaries or returns a CSV download.
