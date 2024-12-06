"""The main Dash page that contains the navigation bar and footer."""
import base64
import datetime
import os

import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask import Blueprint, session
from dash_extensions.enrich import DashProxy, NoOutputTransform

dashMain = Blueprint("dashMain", __name__)

def sales_tool(server):
    """
    Load config and layout of dashboard page.
    """
    # Set up Dash
    dash._dash_renderer._set_react_version('18.2.0')
    
    # Initialize the Dash app with minimal config first
    dash_app = DashProxy(
        name=__name__,
        server=server,
        use_pages=True,
        pages_folder=os.path.abspath(r"movieRatingSystem/dash_main/pages"),  # Make sure this path is correct
        assets_folder=os.path.abspath(r"movieRatingSystem/assets"),
        title="CS4411 Movie Recs",
        routes_pathname_prefix="/movies/",
        transforms=[NoOutputTransform()],
        suppress_callback_exceptions=True,
        assets_ignore='.*\.py',  # Ignore Python files in assets folder
    )

    # Basic layout with error boundary
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(
            id='error-boundary',
            children=[
                dmc.Header(
                    height=60,
                    children=[
                        dmc.Container(
                            fluid=True,
                            children=[
                                dmc.Group(
                                    position="apart",
                                    children=[
                                        dmc.Text("CS4411 Movie Database", size="xl"),
                                        dmc.Group(
                                            children=[
                                                dcc.Link(
                                                    dmc.Button("Search", variant="light"),
                                                    href="/movies/search"
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                dmc.Container(
                    fluid=True,
                    style={"marginTop": 20},
                    children=[
                        dash.page_container
                    ]
                )
            ]
        )
    ])

    # Print registered pages for debugging
    print("Registered Dash pages:", dash.page_registry.keys())
    
    return dash_app.server