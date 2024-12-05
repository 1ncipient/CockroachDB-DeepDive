import os
import dash
import logging
from flask import Flask, redirect, send_from_directory
from movieRatingSystem.logging_config import setup_logging
from movieRatingSystem.dash_main.dash_pages import dashMain as dash_blueprint
from movieRatingSystem.dash_main.dash_pages import sales_tool
from main import main as main_blueprint


# Create application
def create_app(name=None):
    app = Flask(__name__)

    # Disable Flask's default logging
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True

    with app.app_context():
        # Set up logging
        app = setup_logging(app)
        
        # blueprint for non-auth parts of app
        app.register_blueprint(main_blueprint)

        # blueprint for dash testing
        app.register_blueprint(dash_blueprint)

        app = sales_tool(app)
        
        app.logger.info("Application started successfully")
        return app


if __name__ == "__main__":
    app = create_app()
    app.logger.info("Running app")
    app.run(debug=True)
