import os
import dash
from flask import Flask, redirect, send_from_directory

from movieRatingSystem.dash_main.dash_pages import dashMain as dash_blueprint
from movieRatingSystem.dash_main.dash_pages import sales_tool
from main import main as main_blueprint


# Create application
def create_app(name=None):
    app = Flask(__name__)

    with app.app_context():
        # blueprint for non-auth parts of app
        app.register_blueprint(main_blueprint)

        # blueprint for dash testing
        app.register_blueprint(dash_blueprint)

        app = sales_tool(app)
        return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
