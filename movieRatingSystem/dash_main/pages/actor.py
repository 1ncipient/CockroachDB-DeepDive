from dash import Input, Output, State, dash_table, dcc, html, ALL, ctx
import dash
import plotly.express as px
import pandas as pd 
import polars as pl
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()
DATABASE_URL = os.getenv('COCKROACH_DATABASE_URL')
dash.register_page(__name__, path='/actor')

def layout(actorID=None, **other_unknown_query_strings):
    return html.Div(
        children=[
            dmc.LoadingOverlay(id='loading-overlay-actor-info',
                                overlayProps={"radius": "sm", "blur": 2},
                                zIndex=10,
                                visible=True,
                                ),
            html.Button(children='hello', id='test-button-actor', style={'display' : 'None'}),
            html.Span(id='actorID', style={'display' : 'None'},  children=actorID),
            html.Div(id='actor-container'),
        ]
    )   

@dash.callback(
    Output("actor-container", "children"),
    Output('loading-overlay-actor-info', 'visible'),
    Input('test-button-actor', 'n_clicks'),
    State('actorID', 'children'),
)
def showActorInfo(nClicks, actorID):

    specificActor = pd.read_sql(f"SELECT a.\"movieId\", a.profile_path, a.actor_id, a.actor_name, a.character, m.poster_path FROM actors a JOIN movie_metadata m ON a.\"movieId\" = m.\"movieId\" WHERE actor_id = {actorID};", DATABASE_URL)

    actorName = specificActor['actor_name'].unique()[0]
    actorPicture = specificActor['profile_path'].unique()[0]
    actorHTML = html.Div(
        dmc.Center(
            children=[
                dmc.Grid(
                    children=[
                        dmc.GridCol(span=4),
                        dmc.GridCol(
                            children=[
                                dmc.Title(children=f"{actorName}"),
                                dmc.Image(src=f"https://image.tmdb.org/t/p/original{actorPicture}", h=350, w=280),
                            ],
                            span=4
                        ),
                        dmc.GridCol(span=4),
                        dmc.GridCol(
                            children=[
                                dmc.Divider(variant="solid" , style={'margin-top' : '25px', 'margin-bottom' : '25px'}),
                                dmc.Text('Movies Featured in:', size='xl'),
                                dmc.ScrollArea(
                                    w=1300, h=280,
                                    scrollbars='x',
                                    id='actor-container',
                                    children=[
                                        dmc.Flex(
                                            children=[
                                                dmc.Flex(
                                                    children=[
                                                        dmc.Image(src=f"https://image.tmdb.org/t/p/original{actor['poster_path']}" if actor['poster_path'] else "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-4-user-grey-d8fe957375e70239d6abdd549fd7568c89281b2179b5f4470e2e12895792dfa5.svg", h=150, w=100),
                                                        dcc.Link(dmc.Text(actor['character'], w=100), href=f"/info?movieID={actor['movieId']}"),
                                                    ],
                                                    direction='column',
                                                    h=200,
                                                ) for actor in specificActor.to_dict('records')
                                            ],
                                            gap='lg'
                                        )
                                    ]
                                )
                            ],
                            span=12
                        ),                        
                    ],
                )
            ]
        )
    )

    return actorHTML, False

