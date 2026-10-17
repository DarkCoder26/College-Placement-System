import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, abort, make_response
from flask_wtf.csrf import CSRFProtect
from database import init_db, get_db, close_db, create_student, get_student, update_student, delete_student, list_students, dashboard_stats
from analysis import build_analytics, students_csv, analytics_csv

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, instance_path=str(BASE_DIR / "instance"), instance_relative_config=True)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "dev-only-change-this-key"),
    DATABASE=os.environ.get("PLACEMENT_DATABASE", str(BASE_DIR / "instance" / "placement.db")),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)
csrf = CSRFProtect(app)

@app.before_request
def ensure_database():
    init_db(app.config["DATABASE"])

@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)

@app.context_processor
def inject_globals():
    return {"current_year": __import__("datetime").datetime.now().year}

def form_data():
    return {key: (request.form.get(key) or "").strip() for key in
            ("roll_number", "full_name", "department", "graduation_year", "cgpa",
             "placement_status", "company_name", "job_role", "package_lpa")}

def validate_student(data):
    errors = []
    if not data["roll_number"] or len(data["roll_number"]) > 30:
        errors.append("Roll number is required and must be at most 30 characters.")
    if not data["full_name"] or len(data["full_name"]) > 100:
        errors.append("Full name is required and must be at most 100 characters.")
    if not data["department"] or len(data["department"]) > 80:
        errors.append("Department is required and must be at most 80 characters.")
    try:
        year = int(data["graduation_year"])
        if year < 2000 or year > 2100:
            raise ValueError()
    except (ValueError, TypeError):
        errors.append("Graduation year must be a whole year between 2000 and 2100.")
        year = None
    try:
        cgpa = float(data["cgpa"])
        if not 0 <= cgpa <= 10:
            raise ValueError()
    except (ValueError, TypeError):
        errors.append("CGPA must be a number between 0 and 10.")
        cgpa = None
    status = data["placement_status"]
    if status not in ("Placed", "Not Placed"):
        errors.append("Choose a valid placement status.")
    try:
        package = float(data["package_lpa"] or 0)
        if package < 0:
            raise ValueError()
    except (ValueError, TypeError):
        errors.append("Package must be zero or a positive number.")
        package = None
    company, role = data["company_name"], data["job_role"]
    if status == "Placed":
        if not company or len(company) > 100:
            errors.append("Company name is required for placed students (maximum 100 characters).")
        if not role or len(role) > 100:
            errors.append("Job role is required for placed students (maximum 100 characters).")
        if package is None or package <= 0:
            errors.append("Package must be greater than zero for placed students.")
    else:
        company, role, package = "", "", 0.0
    clean = {
        "roll_number": data["roll_number"], "full_name": data["full_name"],
        "department": data["department"], "graduation_year": year, "cgpa": cgpa,
        "placement_status": status, "company_name": company, "job_role": role,
        "package_lpa": package
    }
    return clean, errors

@app.route("/")
def index():
    db = get_db()
    stats = dashboard_stats(db)
    recent = list_students(db, limit=6, sort="created_at", direction="desc")
    analytics_data = build_analytics(db)
    monthly = db.execute("""
        SELECT strftime('%Y-%m', created_at) AS month_key,
               strftime('%b', created_at) AS month_label, COUNT(*) AS total,
               SUM(CASE WHEN placement_status='Placed' THEN 1 ELSE 0 END) AS placed
        FROM students GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month_key DESC LIMIT 12
    """).fetchall()
    monthly = list(reversed(monthly))
    return render_template("index.html", stats=stats, recent=recent,
                           analytics=analytics_data, monthly=monthly)

@app.route("/students")
def students():
    db = get_db()
    filters = {
        "q": request.args.get("q", "").strip(),
        "department": request.args.get("department", "").strip(),
        "status": request.args.get("status", "").strip(),
        "year": request.args.get("year", "").strip(),
        "sort": request.args.get("sort", "name").strip(),
        "direction": request.args.get("direction", "asc").strip().lower()
    }
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    per_page = 10
    rows, total = list_students(db, filters=filters, limit=per_page, offset=(page-1)*per_page, with_count=True)
    departments = [r["department"] for r in db.execute("SELECT DISTINCT department FROM students ORDER BY department")]
    years = [r["graduation_year"] for r in db.execute("SELECT DISTINCT graduation_year FROM students ORDER BY graduation_year DESC")]
    return render_template("students.html", students=rows, filters=filters, departments=departments,
                           years=years, page=page, pages=max(1, (total + per_page - 1)//per_page), total=total)

@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        clean, errors = validate_student(form_data())
        if not errors:
            try:
                create_student(get_db(), clean)
                flash("Student added successfully.", "success")
                return redirect(url_for("students"))
            except Exception as exc:
                if "UNIQUE constraint failed" in str(exc):
                    errors.append("That roll number already exists.")
                else:
                    app.logger.exception("Could not create student")
                    errors.append("The student could not be saved. Please try again.")
        for error in errors:
            flash(error, "error")
        return render_template("add_student.html", student=form_data(), page_title="Add Student"), 400
    return render_template("add_student.html", student={}, page_title="Add Student")

@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    db = get_db()
    student = get_student(db, student_id)
    if not student:
        abort(404)
    if request.method == "POST":
        clean, errors = validate_student(form_data())
        if not errors:
            try:
                update_student(db, student_id, clean)
                flash("Student details updated.", "success")
                return redirect(url_for("students"))
            except Exception as exc:
                if "UNIQUE constraint failed" in str(exc):
                    errors.append("That roll number already exists.")
                else:
                    app.logger.exception("Could not update student")
                    errors.append("The student could not be updated. Please try again.")
        for error in errors:
            flash(error, "error")
        return render_template("add_student.html", student=form_data(), page_title="Edit Student", student_id=student_id), 400
    return render_template("add_student.html", student=student, page_title="Edit Student", student_id=student_id)

@app.route("/students/<int:student_id>/delete", methods=["POST"])
def remove_student(student_id):
    if not delete_student(get_db(), student_id):
        abort(404)
    flash("Student deleted.", "success")
    return redirect(url_for("students"))

@app.route("/analytics")
def analytics():
    data = build_analytics(get_db())
    return render_template("analytics.html", data=data)

@app.route("/reports/students.csv")
def export_students():
    output = students_csv(get_db())
    response = make_response(output)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = 'attachment; filename="college_placement_students.csv"'
    return response

@app.route("/reports/analytics.csv")
def export_analytics():
    output = analytics_csv(build_analytics(get_db()))
    response = make_response(output)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = 'attachment; filename="college_placement_analytics.csv"'
    return response

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    # Debug is opt-in for local development and should never be enabled in production.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG", "0") == "1")
