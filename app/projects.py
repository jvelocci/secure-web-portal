from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app.db import get_db_connection
from psycopg import errors
import csv
from io import StringIO

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")

# A3 -- All Projects
@projects_bp.route("/all", methods=["GET", "POST"])
def sort_projects():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    whitelisted_methods = ["headcount", "total_hours", "project_number"]
    whitelisted_directions = ["ASC", "DESC"]
    
    method = "project_number"
    direction = "ASC"
    if request.method == "POST":  # On sorting options applied 
        method = request.form.get("method", "")
        direction = request.form.get("direction", "")
        # Validate inputs against whitelisted options before querying  
        if method not in whitelisted_methods:
            method = "headcount"
        if direction not in whitelisted_directions:
            direction = "ASC"

    cur.execute(
        f"""
        SELECT
            p.pnumber AS project_number, 
            p.pname AS project_name, 
            d.dname AS owning_department, 
            COUNT(w.essn) AS headcount,
            COALESCE(SUM(w.hours), 0) AS total_hours  
        FROM project p
        JOIN department d ON p.dnum = d.dnumber
        LEFT JOIN works_on w ON p.pnumber = w.pno
        GROUP BY p.pnumber, d.dnumber
        ORDER BY {method} {direction};
        """
    )
    project_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("projects.html", projects=project_list,
                           selected_method=method, selected_direction=direction)

# A4 -- Project Details    
@projects_bp.route("/<pnumber>", methods=["GET", "POST"])
def project_detail(pnumber):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Select all employees on the project and their hours
        cur.execute(
            """
            SELECT 
                e.fname as first_name, 
                e.minit as middle_initial,
                e.lname as last_name, 
                w.hours as hours
            FROM employee e
            JOIN works_on w ON e.ssn = w.essn
            WHERE w.pno = %s
            ORDER BY e.fname;
            """,
            (pnumber,)
        )
        project_details = cur.fetchall()
        
        # Select all employees in the database
        cur.execute(
            """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY e.fname) AS rownum,
                e.fname AS first_name, 
                e.minit AS middle_initial,
                e.lname AS last_name
            FROM employee e;
            """
        )
        all_employees = cur.fetchall()
    except Exception as e:
        flash("An error occurred while fetching project details.", "error")
        print(f"\033[1;91mError fetching project details: {str(e)}\033[0m")

        cur.close()
        conn.close()
        return render_template("project_detail.html",
                           details=project_details,
                           pnumber=pnumber,
                           employees=all_employees)
    
    # A4 Part 2: Employee Upsert Form submission (admin only)
    if request.method == "POST":
        # RBAC: only admins can modify hours
        if session.get("role") != "admin":
            flash("You do not have permission to modify project hours.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("projects.project_detail", pnumber=pnumber))

        employee_n = int(request.form.get("employee", ""))  # using index in case two employees have the same full name
        hours = request.form.get("hours", "")
        try:
            cur.execute(
                """
                SELECT ssn
                FROM employee
                ORDER BY fname
                """
            )
            employee_ssns = cur.fetchall()
            target_ssn = employee_ssns[employee_n - 1][0]  # get the ssn of the employee we want
            # add the employee to works_on for that pnumber, or update their hours 
        
            cur.execute(
                """
                INSERT INTO works_on (essn, pno, hours)
                VALUES (%s, %s, %s)
                ON CONFLICT (essn, pno)
                DO UPDATE SET hours = works_on.hours + EXCLUDED.hours;
                """,
                (target_ssn, pnumber, hours)
            )
            conn.commit()
        except errors.NumericValueOutOfRange:
            conn.rollback()
            print("\033[1;91mError: Cannot add more hours to employee (max hours is 999.9)\033[0m")
            flash("Cannot add more hours to employee (max hours is 999.9 per employee)", "error")
        except Exception as e:
            conn.rollback()
            print(f"\033[1;91mError adding/updating employee hours: {str(e)}\033[0m")
            flash(f"Error adding/updating employee hours", "error")
        cur.close()
        conn.close()
        return redirect(url_for("projects.project_detail", pnumber=pnumber))
    
    cur.close()
    conn.close()
    return render_template("project_detail.html",
                           details=project_details,
                           pnumber=pnumber,
                           employees=all_employees)

@projects_bp.route("/download/<method>/<direction>", methods=["POST"])
def download_projects(method, direction): 
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # RBAC: treat export as an admin-only feature
    if session.get("role") != "admin":
        flash("You do not have permission to download project data.", "error")
        return redirect(url_for("projects.sort_projects"))
    
    whitelisted_methods = ["headcount", "total_hours", "project_number"]
    whitelisted_directions = ["ASC", "DESC"]
    
    # Validate inputs against whitelisted options before querying  
    if method not in whitelisted_methods:
        method = "headcount"
    if direction not in whitelisted_directions:
        direction = "ASC"
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT
            p.pnumber AS project_number, 
            p.pname AS project_name, 
            d.dname AS owning_department, 
            COUNT(w.essn) AS headcount,
            COALESCE(SUM(w.hours), 0) AS total_hours  
        FROM project p
        JOIN department d ON p.dnum = d.dnumber
        LEFT JOIN works_on w ON p.pnumber = w.pno
        GROUP BY p.pnumber, d.dnumber
        ORDER BY {method} {direction};
        """
    )
    project_list = cur.fetchall()
    cur.close()
    conn.close()
    
    # Generate CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Project_Number", "Project_Name", "Owning_Department", "Headcount", "Total_Hours"])
    cw.writerows(project_list)
    output = si.getvalue()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=projects.csv"}
    )
