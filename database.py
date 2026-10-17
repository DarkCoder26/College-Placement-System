import sqlite3
from pathlib import Path
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL UNIQUE CHECK(length(trim(roll_number)) BETWEEN 1 AND 30),
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) BETWEEN 1 AND 100),
    department TEXT NOT NULL CHECK(length(trim(department)) BETWEEN 1 AND 80),
    graduation_year INTEGER NOT NULL CHECK(graduation_year BETWEEN 2000 AND 2100),
    cgpa REAL NOT NULL CHECK(cgpa >= 0 AND cgpa <= 10),
    placement_status TEXT NOT NULL CHECK(placement_status IN ('Placed', 'Not Placed')),
    company_name TEXT NOT NULL DEFAULT '',
    job_role TEXT NOT NULL DEFAULT '',
    package_lpa REAL NOT NULL DEFAULT 0 CHECK(package_lpa >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
      (placement_status = 'Placed' AND length(trim(company_name)) > 0
       AND length(trim(job_role)) > 0 AND package_lpa > 0)
      OR
      (placement_status = 'Not Placed' AND company_name = ''
       AND job_role = '' AND package_lpa = 0)
    )
);
CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(placement_status);
CREATE INDEX IF NOT EXISTS idx_students_year ON students(graduation_year);
"""

def connect_db(path=None):
    db_path = path or current_app.config["DATABASE"]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def get_db():
    if "db" not in g:
        g.db = connect_db()
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(path=None):
    db = connect_db(path)
    try:
        db.executescript(SCHEMA)
        db.commit()
    finally:
        db.close()

def create_student(db, student):
    columns = ("roll_number", "full_name", "department", "graduation_year", "cgpa",
               "placement_status", "company_name", "job_role", "package_lpa")
    db.execute(
        "INSERT INTO students (" + ",".join(columns) + ") VALUES (" +
        ",".join("?" for _ in columns) + ")",
        tuple(student[column] for column in columns)
    )
    db.commit()

def get_student(db, student_id):
    return db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()

def update_student(db, student_id, student):
    columns = ("roll_number", "full_name", "department", "graduation_year", "cgpa",
               "placement_status", "company_name", "job_role", "package_lpa")
    cursor = db.execute(
        "UPDATE students SET " + ",".join(f"{column} = ?" for column in columns) + " WHERE id = ?",
        tuple(student[column] for column in columns) + (student_id,)
    )
    db.commit()
    return cursor.rowcount > 0

def delete_student(db, student_id):
    cursor = db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    return cursor.rowcount > 0

def list_students(db, filters=None, limit=None, offset=0, sort="name", direction="asc", with_count=False):
    filters = filters or {}
    clauses, values = [], []
    q = filters.get("q", "")
    if q:
        clauses.append("(full_name LIKE ? OR roll_number LIKE ?)")
        values.extend([f"%{q}%", f"%{q}%"])
    if filters.get("department"):
        clauses.append("department = ?")
        values.append(filters["department"])
    if filters.get("status") in ("Placed", "Not Placed"):
        clauses.append("placement_status = ?")
        values.append(filters["status"])
    if filters.get("year"):
        try:
            year = int(filters["year"])
            clauses.append("graduation_year = ?")
            values.append(year)
        except (TypeError, ValueError):
            pass
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    allowed_sort = {"name": "full_name", "cgpa": "cgpa", "package": "package_lpa",
                    "status": "placement_status", "created_at": "created_at"}
    order = allowed_sort.get(filters.get("sort", sort), "full_name")
    dir_sql = "DESC" if filters.get("direction", direction).lower() == "desc" else "ASC"
    total = db.execute("SELECT COUNT(*) FROM students" + where, values).fetchone()[0]
    sql = "SELECT * FROM students" + where + f" ORDER BY {order} {dir_sql}, id ASC"
    params = list(values)
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([int(limit), int(offset)])
    rows = db.execute(sql, params).fetchall()
    return (rows, total) if with_count else rows

def dashboard_stats(db):
    row = db.execute("""
      SELECT COUNT(*) total,
       SUM(CASE WHEN placement_status='Placed' THEN 1 ELSE 0 END) placed,
       AVG(CASE WHEN placement_status='Placed' THEN package_lpa END) average_package,
       MAX(CASE WHEN placement_status='Placed' THEN package_lpa END) highest_package,
       COUNT(DISTINCT department) departments
      FROM students
    """).fetchone()
    total = row["total"] or 0
    placed = row["placed"] or 0
    return {
        "total": total, "placed": placed, "not_placed": total - placed,
        "placement_rate": (placed / total * 100) if total else 0,
        "average_package": row["average_package"] or 0,
        "highest_package": row["highest_package"] or 0,
        "departments": row["departments"] or 0
    }
