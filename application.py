import os
from datetime import timedelta
from flask import Flask, redirect, session, url_for, request
import logging

from movieRatingSystem.dash_main.dash_pages import dashMain as dash_blueprint
from movieRatingSystem.dash_main.dash_pages import sales_tool
from main import main as main_blueprint
from auth_blueprint import auth as auth_blueprint
from movieRatingSystem.AuthManager import AuthManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_manager = AuthManager(conn_string=os.getenv("DATABASE_URL"))

def create_app(name=None):
    app = Flask(__name__)
    app.secret_key = "super-secret-key"
    
    # Session config
    app.config.update(
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SEND_FILE_MAX_AGE_DEFAULT=0
    )
    
    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(main_blueprint)
    app.register_blueprint(dash_blueprint)

    # Initialize Dash
    app = sales_tool(app)
    
    @app.before_request
    def check_login():
        # Paths that don't require authentication
        exempt_paths = [
            "/auth/login",
            "/auth/register",
            "/auth/logout",
            "/auth/",
            "/static/",
            "/favicon.ico"
        ]

        # Skip auth check for exempt paths
        if any(request.path.startswith(path) for path in exempt_paths):
            return None

        # Check if user is authenticated
        if 'user_id' not in session:
            # Allow certain Dash asset requests without redirect
            if request.path.startswith('/movies/_dash-') or request.path.startswith('/movies/assets/'):
                if request.headers.get('Accept') == 'application/json':
                    return '', 204
            return redirect(url_for('auth.login'))

        return None

    @app.after_request
    def after_request(response):
        # Set proper content type for Dash JSON responses
        if request.path.startswith('/movies/_dash-') and not response.content_type:
            response.content_type = 'application/json'
        return response

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)