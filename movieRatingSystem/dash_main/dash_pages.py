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
from movieRatingSystem.styles.common import COLORS

dashMain = Blueprint("dashMain", __name__)

def create_nav_link(label, href):
    return dcc.Link(
        dmc.Text(
            label,
            size="sm",
            c=COLORS['text'],
            style={
                'transition': 'color 0.2s ease',
                '&:hover': {'color': COLORS['primary']}
            }
        ),
        href=href,
        style={'textDecoration': 'none'},
        refresh=True
    )

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
        title="MovieLens Explorer",
        url_base_pathname="/",  # Root path for the Dash app
        external_stylesheets=dmc.styles.ALL,
    )

    # Create the navigation bar
    navbar = dmc.Container(
        fluid=True,
        style={
            'backgroundColor': COLORS['surface'],
            'borderBottom': '1px solid #e2e8f0',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'right': 0,
            'height': '70px',
            'display': 'flex',
            'alignItems': 'center',
            'padding': '0 24px',
            'zIndex': 100
        },
        children=[
            # Logo/Brand
            create_nav_link(
                dmc.Title(
                    "MovieLens",
                    order=1,
                    style={
                        'color': COLORS['primary'],
                        'fontSize': '24px',
                        'letterSpacing': '-0.5px'
                    }
                ),
                '/'
            ),
            # Navigation Links
            dmc.Group(
                justify="right",
                gap="xl",
                style={'flex': 1},
                children=[
                    create_nav_link("Home", "/home/"),
                    create_nav_link("Movies", "/movies/"),
                    # Add this new html.Div for the logout button
                    html.Div(
                        dcc.Link(
                            dmc.Button(
                                "Logout",
                                leftSection=[DashIconify(icon="carbon:logout")],  # Changed from leftIcon to leftSection
                                variant="filled",
                                color="red",
                                size="sm",
                                styles={'root': {'backgroundColor': '#dc2626', '&:hover': {'backgroundColor': '#b91c1c'}}}
                            ),
                            href="/auth/logout",
                            refresh=True
                        )
                    )
                ]
            )
        ]
    )

    dash_app.layout = dmc.MantineProvider(
        theme={
            'colorScheme': 'light',
            'primaryColor': 'blue',
            'components': {
                'Button': {'styles': {'root': {'fontWeight': 500}}},
                'TextInput': {'styles': {'input': {'backgroundColor': COLORS['surface']}}},
                'Select': {'styles': {'input': {'backgroundColor': COLORS['surface']}}},
            }
        },
        children=[
            navbar,
            dmc.Container(
                fluid=True,
                pt=70,  # Add padding top to account for fixed navbar
                style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'},
                children=dash.page_container
            )
        ]
    )

    return dash_app.server

