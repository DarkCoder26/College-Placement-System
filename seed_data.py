"""Optional: insert 12 fictional demonstration records once. Run: python seed_data.py"""
import os
from pathlib import Path
from database import connect_db, init_db

DB_PATH = os.environ.get("PLACEMENT_DATABASE", str(Path(__file__).resolve().parent / "instance" / "placement.db"))
SAMPLE = [
("BCA2025001","Aarav Sharma","Computer Applications",2025,8.6,"Placed","Northstar Digital","Python Developer",6.5),
("BCA2025002","Meera Kapoor","Computer Applications",2025,9.1,"Placed","BluePeak Systems","Data Analyst",8.2),
("BCA2025003","Kabir Singh","Information Technology",2025,7.8,"Placed","CedarCloud Labs","QA Engineer",4.8),
("BCA2025004","Ananya Verma","Information Technology",2025,8.2,"Not Placed","","",0),
("BCA2025005","Ishaan Gupta","Commerce & IT",2025,7.1,"Placed","MapleWorks Tech","Support Engineer",3.6),
("BCA2025006","Simran Kaur","Computer Applications",2026,8.9,"Placed","BluePeak Systems","Junior Developer",7.4),
("BCA2025007","Reyansh Patel","Information Technology",2026,6.8,"Not Placed","","",0),
("BCA2025008","Diya Malhotra","Commerce & IT",2026,8.0,"Placed","Northstar Digital","Business Analyst",5.2),
("BCA2025009","Arjun Mehta","Computer Applications",2026,7.6,"Not Placed","","",0),
("BCA2025010","Navya Joshi","Information Technology",2026,9.3,"Placed","OrbitLeaf Analytics","Data Engineer",9.5),
("BCA2025011","Vivaan Rao","Commerce & IT",2025,6.9,"Not Placed","","",0),
("BCA2025012","Sara Gill","Computer Applications",2025,8.4,"Placed","CedarCloud Labs","Web Developer",5.8),
]
def main():
    init_db(DB_PATH)
    db = connect_db(DB_PATH)
    try:
        existing = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if existing:
            print(f"Database already contains {existing} student(s); no sample rows inserted.")
            return
        db.executemany("""INSERT INTO students
        (roll_number,full_name,department,graduation_year,cgpa,placement_status,company_name,job_role,package_lpa)
        VALUES (?,?,?,?,?,?,?,?,?)""", SAMPLE)
        db.commit()
        print(f"Inserted {len(SAMPLE)} fictional sample students into {DB_PATH}")
    finally:
        db.close()
if __name__ == "__main__":
    main()
