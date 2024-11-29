"""Creates Home page that is viewing right after landing page."""
import base64
import os
import warnings

import dash
import dash_mantine_components as dmc
from dash import dcc, html


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
                        dcc.Link(dmc.Chip("Search", value="booktobill_chip"), href="/movies/search"),
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
