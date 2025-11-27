import os
from flask import Flask
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # import and register blueprints
    from app.auth import auth_bp
    from app.employees import employees_bp
    from app.projects import projects_bp
    from app.employeeManagement import employee_management_bp
    from app.managers import managers_bp  # ADD THIS LINE

    app.register_blueprint(auth_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(employee_management_bp)
    app.register_blueprint(managers_bp)  # ADD THIS LINE

    return app
