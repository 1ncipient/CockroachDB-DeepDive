import os
import dash
import logging
from datetime import timedelta
from flask import Flask, redirect, session, url_for, request
from movieRatingSystem.logging_config import setup_logging
from movieRatingSystem.dash_main.dash_pages import dashMain as dash_blueprint
from movieRatingSystem.dash_main.dash_pages import sales_tool
from movieRatingSystem.auth.auth import auth as auth_blueprint
from main import main as main_blueprint

def create_app(name=None):
    app = Flask(__name__,
                static_folder='movieRatingSystem/static',
                template_folder='movieRatingSystem/templates')
    
    app.secret_key = "super-secret-key"
    
    # Enable debug mode
    # app.debug = True
    
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    # Set this to False to enable logging
    log.disabled = True
    
    # Session config
    app.config.update(
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SEND_FILE_MAX_AGE_DEFAULT=0
    )

    with app.app_context():
        # Set up logging
        app = setup_logging(app)
        
        # Register blueprints
        app.register_blueprint(auth_blueprint, url_prefix="/auth")
        app.register_blueprint(main_blueprint)
        app.register_blueprint(dash_blueprint)

        app = sales_tool(app)
        
        @app.route("/")
        def index():
            return redirect(url_for("auth.login"))
        
        @app.before_request
        def check_login():
            exempt_paths = [
                "/auth/login",
                "/auth/register",
                "/auth/logout",
                "/auth/",
                "/static/",
                "/favicon.ico"
            ]

            if any(request.path.startswith(path) for path in exempt_paths):
                return None

            if 'user_id' not in session:
                if request.path.startswith('/movies/_dash-') or request.path.startswith('/movies/assets/'):
                    if request.headers.get('Accept') == 'application/json':
                        return '', 204
                return redirect(url_for('auth.login'))

            return None

        @app.errorhandler(Exception)
        def handle_exception(e):
            app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return str(e), 500

        return app

if __name__ == "__main__":
    app = create_app()
    app.logger.info("Running app...")
    app.run(debug=True)