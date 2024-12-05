"""The main Dash page that contains the navigation bar and footer."""
import base64
import datetime
import os

import dash
import dash_mantine_components as dmc
from dash import ALL, Dash, Input, Output, html, dcc, State, ctx
from dash_iconify import DashIconify
from flask import Blueprint
from dash_extensions.enrich import DashProxy

dashMain = Blueprint("dashMain", __name__)

toolIcons = {'Home' : "antd-home", 'Zendesk' : "antd-comment", 'Idmr' : 'md-build',
            'Tech-pubs' : 'antd-read'
            }


def sales_tool(server):
    """
    Load config and layout of dashboard page.

    Args:
        server: The configuration for the server
    Returns:
        The navbar, page content and footer
    """
    dash._dash_renderer._set_react_version('18.2.0')
    dash_app = DashProxy(
        name=__name__,
        pages_folder="pages",
        use_pages=True,
        server=server,
        assets_folder=os.path.abspath(r"movieRatingSystem/assets"),
        title="CS4411 Movie Recs",
        routes_pathname_prefix="/movies/",
        external_stylesheets=dmc.styles.ALL
    )

    # Filter out the home page and adjust it
    filtered_dict = {}

    # Create filter dict and create the home page with custom url to the home page
    for page, innerDict in dash.page_registry.items():
        filtered_dict[page] = innerDict

    dash_app.layout = dmc.MantineProvider(
            children=[
                dcc.Link(dmc.Text('CS4411 Movie Database', style={'margin' : '25px'}), href='/movies/search/'),
                dash.page_container,
            ],
        )


    return dash_app.server

