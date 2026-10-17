import pandas as pd
from database import list_students

EXPORT_COLUMNS = ["id", "roll_number", "full_name", "department", "graduation_year",
                  "cgpa", "placement_status", "company_name", "job_role", "package_lpa", "created_at"]

def dataframe_from_db(db):
    rows = db.execute("SELECT " + ",".join(EXPORT_COLUMNS) + " FROM students ORDER BY id").fetchall()
    return pd.DataFrame([dict(row) for row in rows], columns=EXPORT_COLUMNS)

def build_analytics(db):
    df = dataframe_from_db(db)
    total = len(df)
    placed_df = df[df["placement_status"] == "Placed"] if total else df
    placed = len(placed_df)
    department_rows = []
    if total:
        for department, group in df.groupby("department", dropna=False):
            count = len(group)
            placed_count = int((group["placement_status"] == "Placed").sum())
            department_rows.append({
                "department": department, "total": count, "placed": placed_count,
                "not_placed": count - placed_count,
                "placement_rate": (placed_count / count * 100) if count else 0
            })
    company_rows = []
    if placed:
        company_counts = placed_df.groupby("company_name").size().sort_values(ascending=False)
        company_rows = [{"company": str(name), "count": int(count)} for name, count in company_counts.items()]
    year_rows = []
    if total:
        for year, group in df.groupby("graduation_year"):
            count = len(group)
            placed_count = int((group["placement_status"] == "Placed").sum())
            year_rows.append({"year": int(year), "total": count, "placed": placed_count,
                              "placement_rate": placed_count / count * 100 if count else 0})
    ranges = [(0,3,"0–3"),(3,6,"3–6"),(6,9,"6–9"),(9,12,"9–12"),(12,15,"12–15"),(15,float("inf"),"15+")]
    package_bands = []
    for low, high, label in ranges:
        if not placed: count = 0
        elif high == float("inf"): count = int((placed_df["package_lpa"] >= low).sum())
        else: count = int(((placed_df["package_lpa"] >= low) & (placed_df["package_lpa"] < high)).sum())
        package_bands.append({"label": label, "count": count})
    return {
        "total": total, "placed": placed, "not_placed": total - placed,
        "placement_rate": placed / total * 100 if total else 0,
        "average_package": float(placed_df["package_lpa"].mean()) if placed else 0,
        "highest_package": float(placed_df["package_lpa"].max()) if placed else 0,
        "departments": department_rows, "companies": company_rows, "years": year_rows,
        "package_bands": package_bands
    }

def students_csv(db):
    df = dataframe_from_db(db)
    # UTF-8 BOM improves compatibility with Microsoft Excel.
    return "\ufeff" + df.to_csv(index=False, lineterminator="\n")

def analytics_csv(data):
    rows = []
    for item in data["departments"]:
        rows.append({"section": "Department", "group": item["department"], "total": item["total"],
                     "placed": item["placed"], "placement_rate_percent": round(item["placement_rate"], 2),
                     "average_package_lpa": ""})
    for item in data["companies"]:
        rows.append({"section": "Company", "group": item["company"], "total": item["count"],
                     "placed": item["count"], "placement_rate_percent": "", "average_package_lpa": ""})
    for item in data["years"]:
        rows.append({"section": "Graduation year", "group": item["year"], "total": item["total"],
                     "placed": item["placed"], "placement_rate_percent": round(item["placement_rate"], 2),
                     "average_package_lpa": ""})
    if not rows:
        rows = [{"section": "Summary", "group": "No data", "total": 0, "placed": 0,
                 "placement_rate_percent": 0, "average_package_lpa": 0}]
    return "\ufeff" + pd.DataFrame(rows).to_csv(index=False, lineterminator="\n")
