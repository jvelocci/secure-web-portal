from flask import Blueprint, render_template, request, session, redirect, url_for
from app.db import get_db_connection

employees_bp = Blueprint("employees", __name__)


@employees_bp.route("/")
def home():
   
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    
    dept = request.args.get("department", "").strip()
    name = request.args.get("name", "").strip()
    sort = request.args.get("sort", "name_asc")

    
    sort_options = {
        "name_asc": "full_name ASC",
        "name_desc": "full_name DESC",
        "hours_asc": "total_hours ASC",
        "hours_desc": "total_hours DESC",
    }
    order_by = sort_options.get(sort, "full_name ASC")

   
    conditions = []
    params = []

    if dept:
        # Filter by department number (Dnumber)
        conditions.append("d.Dnumber = %s")
        params.append(dept)

    if name:
        # Case-insensitive match on full name
        conditions.append(
            "(e.Fname || ' ' || e.Minit || ' ' || e.Lname) ILIKE %s"
        )
        params.append(f"%{name}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # --- Main employee overview query ---
    sql = f"""
        WITH dep_counts AS (
            SELECT Essn, COUNT(*) AS dependent_count
            FROM Dependent
            GROUP BY Essn
        ),
        proj_stats AS (
            SELECT Essn,
                   COUNT(DISTINCT Pno) AS project_count,
                   SUM(Hours) AS total_hours
            FROM Works_On
            GROUP BY Essn
        )
        SELECT
            e.Ssn,
            e.Fname || ' ' || e.Minit || '. ' || e.Lname AS full_name,
            d.Dname AS department_name,
            COALESCE(dc.dependent_count, 0) AS num_dependents,
            COALESCE(ps.project_count, 0)    AS num_projects,
            COALESCE(ps.total_hours, 0)      AS total_hours
        FROM Employee e
        LEFT JOIN Department d ON e.Dno = d.Dnumber
        LEFT JOIN dep_counts dc ON dc.Essn = e.Ssn
        LEFT JOIN proj_stats ps ON ps.Essn = e.Ssn
        {where_clause}
        ORDER BY {order_by}
    """

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    employees = cur.fetchall()
    cur.close()
    conn.close()

    # --- Load departments for dropdown ---
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Dnumber, Dname FROM Department ORDER BY Dname;")
    departments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "home_employees.html",
        employees=employees,
        departments=departments,
        current_dept=dept,
        current_name=name,
        current_sort=sort,
    )
