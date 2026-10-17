import os
import tempfile
import pytest
from app import app as flask_app
from database import init_db, connect_db
from analysis import build_analytics

@pytest.fixture()
def client():
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)
    init_db(path)
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, DATABASE=path, SECRET_KEY="test-secret")
    with flask_app.test_client() as client:
        yield client
    os.unlink(path)

def payload(**overrides):
    data = dict(roll_number="BCA001", full_name="Asha Test", department="Computer Applications",
                graduation_year="2025", cgpa="8.5", placement_status="Placed",
                company_name="Fictional Labs", job_role="Developer", package_lpa="6.5")
    data.update(overrides)
    return data

def add(client, **overrides):
    return client.post("/students/add", data=payload(**overrides), follow_redirects=True)

def test_startup_dashboard_and_empty_database(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Total students" in response.data
    assert b"No student records yet" in response.data

def test_add_valid_student_and_dashboard_calculations(client):
    response = add(client)
    assert response.status_code == 200
    assert b"Student added successfully" in response.data
    response = client.get("/")
    assert b"100.0%" in response.data
    assert b"6.50" in response.data

def test_duplicate_roll_number_rejected(client):
    add(client)
    response = add(client, full_name="Duplicate Person")
    assert response.status_code == 400
    assert b"already exists" in response.data

def test_invalid_cgpa_rejected(client):
    response = add(client, cgpa="11")
    assert response.status_code == 400
    assert b"CGPA must be a number" in response.data

def test_negative_package_rejected(client):
    response = add(client, package_lpa="-2")
    assert response.status_code == 400
    assert b"Package must be zero or a positive number" in response.data

def test_search_and_filter(client):
    add(client)
    add(client, roll_number="BCA002", full_name="Rohan Example", placement_status="Not Placed",
        company_name="", job_role="", package_lpa="0", department="Information Technology")
    assert b"Asha Test" in client.get("/students?q=Asha").data
    response = client.get("/students?status=Not+Placed")
    assert b"Rohan Example" in response.data and b"Asha Test" not in response.data
    assert b"Information Technology" in client.get("/students?department=Information+Technology").data

def test_update_and_delete(client):
    add(client)
    with flask_app.app_context():
        db = connect_db(flask_app.config["DATABASE"])
        student_id = db.execute("SELECT id FROM students").fetchone()[0]
        db.close()
    response = client.post(f"/students/{student_id}/edit", data=payload(full_name="Asha Updated"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Asha Updated" in client.get("/students").data
    response = client.post(f"/students/{student_id}/delete", data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"No matching students" in response.data

def test_analytics_formulas_and_empty_data(client):
    with flask_app.app_context():
        db = connect_db(flask_app.config["DATABASE"])
        data = build_analytics(db)
        assert data["total"] == 0 and data["placement_rate"] == 0
        db.close()
    add(client)
    add(client, roll_number="BCA002", placement_status="Not Placed", company_name="", job_role="", package_lpa="0")
    with flask_app.app_context():
        db = connect_db(flask_app.config["DATABASE"])
        data = build_analytics(db)
        assert data["total"] == 2
        assert data["placed"] == 1
        assert data["placement_rate"] == 50
        assert data["average_package"] == 6.5
        db.close()

def test_csv_exports(client):
    add(client)
    response = client.get("/reports/students.csv")
    assert response.status_code == 200
    assert b"roll_number" in response.data and b"BCA001" in response.data
    response = client.get("/reports/analytics.csv")
    assert response.status_code == 200
    assert b"Department" in response.data

def test_unknown_url_and_analytics_page(client):
    assert client.get("/not-a-route").status_code == 404
    assert client.get("/analytics").status_code == 200
    assert client.get("/about").status_code == 200
