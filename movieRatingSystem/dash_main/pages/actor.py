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
from movieRatingSystem.utils.db_utils import with_db_session, get_actor_info
from movieRatingSystem.styles.common import COLORS, STYLES
from movieRatingSystem.config.database import db_config
from movieRatingSystem.logging_config import get_logger
from movieRatingSystem.utils.export_query_data import QueryExporter

logger = get_logger()

dash.register_page(__name__, path='/actor')

def layout(actorID=None, db_type='cockroach', **other_unknown_query_strings):
    return html.Div(
        children=[
            dmc.LoadingOverlay(
                id='loading-overlay-actor-info',
                overlayProps={"radius": "sm", "blur": 2},
                zIndex=10,
                visible=True,
            ),
            html.Button(children='hello', id='test-button-actor', style={'display': 'None'}),
            html.Span(id='actorID', style={'display': 'None'}, children=actorID),
            html.Span(id='db-type', style={'display': 'None'}, children=db_type),
            dcc.Store(id='query-info'),
            dmc.Paper(
                p="md",
                shadow="sm",
                withBorder=True,
                children=[
                    dmc.Group(
                        justify="space-between",
                        children=[
                            dmc.Text("Query Performance", fw=500),
                            dmc.HoverCard(
                                withArrow=True,
                                width=600,
                                shadow="md",
                                children=[
                                    dmc.HoverCardTarget(
                                        dmc.ActionIcon(
                                            DashIconify(icon="ph:info"),
                                            size="lg",
                                            variant="subtle",
                                            color="gray",
                                        )
                                    ),
                                    dmc.HoverCardDropdown(
                                        id='query-info-hover',
                                        children=[
                                            dmc.Code("Loading query information...", color="red")
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    dmc.Space(h=10),
                    dmc.Text(id='performance-metrics'),
                ]
            ),
            dmc.Space(h=20),
            html.Div(id='actor-container'),
        ]
    )

@dash.callback(
    [
        Output("actor-container", "children"),
        Output('loading-overlay-actor-info', 'visible'),
        Output('query-info', 'data', allow_duplicate=True),
        Output('performance-metrics', 'children', allow_duplicate=True),
        Output('query-info-hover', 'children', allow_duplicate=True),
    ],
    Input('test-button-actor', 'n_clicks'),
    [
        State('actorID', 'children'),
        State('db-type', 'children'),
    ],
    prevent_initial_call='initial_duplicate',
)
def show_actor_info(nClicks, actorID, db_type):
    """Show actor information using the specified database."""
    try:
        # Create a session with the specified database
        session = db_config.create_session(db_type)
        start_time = datetime.datetime.now()
        
        # Get actor details and movies
        actor_data = get_actor_info(session, actorID)
        if not actor_data:
            return html.Div("Actor not found"), False, None, "", ""
        
        query_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Create query info for export
        query_exporter = QueryExporter(output_file=f"{db_type}_actor_info_history.json")
        query_info = {
            'query_time': f"{query_time:.3f}s",
            'total_results': actor_data['total_movies'],
            'actor_id': actorID,
            'db_type': db_type,
            'query_statement': actor_data['movies_query_statement']
        }
        
        query_exporter.add_query(
            statement=query_info['query_statement'],
            query_time=query_info['query_time'],
            result_count=actor_data['total_movies'],
            sql_explanation="actor info query"
        )
        
        # Create the actor info display
        actor_html = dmc.Container(
            size="xl",
            children=[
                dmc.Paper(
                    p="xl",
                    radius="md",
                    withBorder=True,
                    style={'backgroundColor': COLORS['surface']},
                    children=[
                        # Actor header
                        dmc.Title(
                            actor_data['actor']['name'],
                            order=1,
                            style={'color': COLORS['text'], 'textAlign': 'center'}
                        ),
                        dmc.Space(h=20),
                        
                        # Actor content
                        dmc.Grid(
                            children=[
                                # Profile image
                                dmc.GridCol(
                                    span=4,
                                    children=[
                                        dmc.Image(
                                            src=f"https://image.tmdb.org/t/p/w500{actor_data['actor']['profile_path']}" if actor_data['actor'].get('profile_path') else "https://via.placeholder.com/500x750",
                                            radius="md",
                                            style={'width': '100%'}
                                        ),
                                    ]
                                ),
                                
                                # Actor details
                                dmc.GridCol(
                                    span=8,
                                    children=[
                                        dmc.Text(
                                            f"Appeared in {actor_data['total_movies']} movies",
                                            size="lg",
                                            fw=700,
                                            style={'color': COLORS['text']}
                                        ),
                                        dmc.Space(h=20),
                                        
                                        # Movie appearances
                                        dmc.Title(
                                            "Movie Appearances",
                                            order=2,
                                            style={'color': COLORS['text']}
                                        ),
                                        dmc.Space(h=10),
                                        dmc.SimpleGrid(
                                            cols=3,
                                            spacing="lg",
                                            children=[
                                                dmc.Paper(
                                                    p="md",
                                                    radius="md",
                                                    withBorder=True,
                                                    children=[
                                                        dmc.Image(
                                                            src=f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get('poster_path') else "https://via.placeholder.com/200x300",
                                                            h=200,
                                                            fit="cover",
                                                            radius="md"
                                                        ),
                                                        dmc.Space(h=10),
                                                        dmc.Text(
                                                            movie['title'],
                                                            fw=700,
                                                            style={'color': COLORS['text']}
                                                        ),
                                                        dmc.Text(
                                                            f"Released: {movie['release_date'][:4] if movie.get('release_date') else 'N/A'}",
                                                            size="sm",
                                                            c="dimmed",
                                                        ),
                                                        dmc.Space(h=10),
                                                        dcc.Link(
                                                            dmc.Button(
                                                                "View Movie",
                                                                variant="light",
                                                                fullWidth=True,
                                                                size="sm"
                                                            ),
                                                            href=f"/info?movieID={movie['movieId']}&db_type={db_type}"
                                                        )
                                                    ]
                                                )
                                                for movie in actor_data['movies']
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                )
            ]
        )
        
        # Create performance metrics
        metrics = [
            f"Total Time: {query_info['query_time']}",
            f"Database: {db_type.upper()}"
        ]
        
        # Create query info hover content
        hover_content = [
            dmc.Text("Query Information:", size="sm", fw=700),
            dmc.Space(h=5),
            html.Div([
                dmc.Text("Actor Movies Query:", size="sm", fw=500),
                dmc.Code(
                    query_info['query_statement'],
                    block=True,
                    color="blue",
                    style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
                ),
                dmc.Space(h=10)
            ]),
            dmc.Text("Performance Summary:", size="sm", fw=500),
            dmc.Code(
                f"Actor ID: {actorID}\n"
                f"Database: {db_type}\n"
                f"Total Time: {query_info['query_time']}\n"
                f"Total Movies: {query_info['total_results']}",
                block=True,
                color="green",
                style={'whiteSpace': 'pre-wrap'}
            )
        ]
        
        session.close()
        
        return actor_html, False, query_info, " | ".join(metrics), hover_content
        
    except Exception as e:
        logger.error(f"Error showing actor info: {str(e)}", exc_info=True)
        return html.Div(f"Error loading actor information: {str(e)}"), False, None, "", ""

