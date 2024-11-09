"""Creates Home page that is viewing right after landing page."""
import base64
import os
import warnings

import dash
import dash_mantine_components as dmc
from dash import dcc, html


def get_svg_logo(imageName):
    """
    Read the name of the SVG file and loads it as an image.

    Args:
        imageName: Name of the SVG file
    Returns:
        File as an image option
    """
    with open(os.path.abspath(r"dashboards/assets/" + imageName), "rb") as f:
        encoded_logo = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded_logo}"


dash.register_page(__name__, path="/")

first_row = html.Div(
    className="h-screen flex items-center justify-center",
    children=[
        html.Div(
            className="grid grid-rows-2 pl-4 pr-4 pt-4",
            style={
                "background-color": "rgba(179,195,202,0.5)",
                "backdrop-filter": "blur(10px)",
            },
            children=[
                html.Div(className="pb-4", children=[html.H2("Please Use The Navbar To Navigate To A Page!")]),
                html.Div(
                    className="flex justify-around",
                    children=[
                        html.H4("Frequently visited pages: "),
                        dcc.Link(dmc.Chip("Book To Bill", value="booktobill_chip"), href="/dashboards/dashboard-booktobill"),
                        dcc.Link(dmc.Chip("Analytics", value="analytics_chip"), href="/dashboards/dashboard-analytics"),
                        dcc.Link(dmc.Chip("Triage", value="Triage_chip"), href="/dashboards/triage"),
                        dcc.Link(dmc.Chip("Transition", value="Transition_chip"), href="/dashboards/transition"),
                    ],
                ),
            ],
        ),
    ],
)

layout = html.Div(
    [
        first_row,
    ],
)
