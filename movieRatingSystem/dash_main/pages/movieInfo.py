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
from movieRatingSystem.utils.db_utils import with_db_session, get_movie_by_id, get_movie_credits, get_similar_movies
from movieRatingSystem.styles.common import COLORS, STYLES
from movieRatingSystem.config.database import db_config
from movieRatingSystem.logging_config import get_logger
from movieRatingSystem.utils.export_query_data import QueryExporter

logger = get_logger()

dash.register_page(__name__, path='/info')

def layout(movieID=None, db_type='cockroach', **other_unknown_query_strings):
    return html.Div(
        children=[
            dmc.LoadingOverlay(
                id='loading-overlay-movie-info',
                overlayProps={"radius": "sm", "blur": 2},
                zIndex=10,
                visible=True,
            ),
            html.Button(children='hello', id='test-button', style={'display': 'None'}),
            html.Span(id='movieID', style={'display': 'None'}, children=movieID),
            html.Span(id='db-type', style={'display': 'None'}, children=db_type),
            dcc.Store(id='movie-recommend-data'),
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
            html.Div(id='movie-container'),
        ]
    )

@dash.callback(
    [
        Output("movie-container", "children"),
        Output('movie-recommend-data', 'data'),
        Output('loading-overlay-movie-info', 'visible'),
        Output('query-info', 'data', allow_duplicate=True),
        Output('performance-metrics', 'children', allow_duplicate=True),
        Output('query-info-hover', 'children', allow_duplicate=True),
    ],
    Input('test-button', 'n_clicks'),
    [
        State('movieID', 'children'),
        State('db-type', 'children'),
    ],
    prevent_initial_call='initial_duplicate',
)
def show_movie_info(nclicks, movieID, db_type):
    """Show movie information using the specified database."""
    try:
        # Create a session with the specified database
        session = db_config.create_session(db_type)
        total_start_time = datetime.datetime.now()
        
        # Get movie details
        movie_info_start = datetime.datetime.now()
        movie_info = get_movie_by_id(session, movieID)
        movie_info_time = (datetime.datetime.now() - movie_info_start).total_seconds()
        
        if not movie_info:
            return html.Div("Movie not found"), None, False, None, "", ""
        
        # Get movie credits
        credits_start = datetime.datetime.now()
        movie_credits = get_movie_credits(session, movieID)
        credits_time = (datetime.datetime.now() - credits_start).total_seconds()
        
        # Get similar movies
        similar_start = datetime.datetime.now()
        similar_movies = get_similar_movies(session, movieID, limit=18)
        similar_time = (datetime.datetime.now() - similar_start).total_seconds()
        
        total_time = (datetime.datetime.now() - total_start_time).total_seconds()
        
        # Create query info for export
        query_exporter = QueryExporter(output_file=f"{db_type}_movie_info_history.json")
        query_info = {
            'query_times': {
                'movie_info': f"{movie_info_time:.3f}s",
                'credits': f"{credits_time:.3f}s",
                'similar_movies': f"{similar_time:.3f}s",
                'total': f"{total_time:.3f}s"
            },
            'total_results': 1,
            'movie_id': movieID,
            'db_type': db_type,
            'query_statements': {
                'movie_info': movie_info['movie_query_statement'],
                'credits': movie_credits['credits_query_statement'],
                'high_score_movies': similar_movies['high_score_movies_query_statement'],
                'similar_genres': similar_movies['similar_genres_query_statement'],
                'movies_with_companies': similar_movies['movies_with_companies_query_statement']
            }
        }
        query_exporter.add_query(
            statement=str(query_info['query_statements']),
            query_time=query_info['query_times']['total'],
            result_count=1,
            sql_explanation="Retrieves movie details, credits, and finds similar movies based on genre overlap"
        )
        
        # Create the movie info display
        movie_html = dmc.Container(
            size="xl",
            children=[
                dmc.Paper(
                    p="xl",
                    radius="md",
                    withBorder=True,
                    style={'backgroundColor': COLORS['surface']},
                    children=[
                        # Movie header
                        dmc.Group(
                            justify="space-between",
                            children=[
                                dmc.Title(
                                    f"{movie_info['title']} ({movie_info['release_date'].year})",
                                    order=1,
                                    style={'color': COLORS['text']}
                                ),
                                dmc.Badge(
                                    f"{movie_info['vote_average']:.1f}",
                                    size="xl",
                                    radius="xl",
                                    color="green" if movie_info['vote_average'] >= 7 else "orange"
                                ),
                            ]
                        ),
                        dmc.Space(h=20),
                        
                        # Movie content
                        dmc.Grid(
                            children=[
                                # Poster and links
                                dmc.GridCol(
                                    span=3,
                                    children=[
                                        dmc.Image(
                                            src=f"https://image.tmdb.org/t/p/w500{movie_info['poster_path']}",
                                            radius="md",
                                            style={'width': '100%'}
                                        ),
                                        dmc.Space(h=10),
                                        dmc.SimpleGrid(
                                            cols=2,
                                            spacing="sm",
                                            children=[
                                                dmc.Anchor(
                                                    dmc.Button(
                                                        "IMDB",
                                                        leftSection=DashIconify(icon="simple-icons:imdb"),
                                                        variant="outline",
                                                        color="yellow",
                                                        fullWidth=True
                                                    ),
                                                    href=f"https://www.imdb.com/title/tt{movie_info.get('imdbId', '')}",
                                                    target="_blank"
                                                ),
                                                dmc.Anchor(
                                                    dmc.Button(
                                                        "TMDB",
                                                        leftSection=DashIconify(icon="simple-icons:themoviedatabase"),
                                                        variant="outline",
                                                        color="blue",
                                                        fullWidth=True
                                                    ),
                                                    href=f"https://www.themoviedb.org/movie/{movie_info.get('tmdbId', '')}",
                                                    target="_blank"
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                
                                # Movie details
                                dmc.GridCol(
                                    span=9,
                                    children=[
                                        # Overview section
                                        dmc.Paper(
                                            p="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Text("Overview", fw=700, size="lg", mb="md"),
                                                dmc.Text(movie_info['overview'], size="md", style={'color': COLORS['text']}),
                                            ]
                                        ),
                                        dmc.Space(h=20),
                                        
                                        # Movie details grid
                                        dmc.SimpleGrid(
                                            cols=2,
                                            spacing="lg",
                                            children=[
                                                # Left column
                                                dmc.Stack(
                                                    children=[
                                                        # Genres
                                                        dmc.Paper(
                                                            p="md",
                                                            withBorder=True,
                                                            children=[
                                                                dmc.Text("Genres", fw=700, mb="sm"),
                                                                dmc.Group(
                                                                    gap="xs",
                                                                    children=[
                                                                        dmc.Badge(genre, size="lg")
                                                                        for genre in movie_info['genres']
                                                                    ]
                                                                )
                                                            ]
                                                        ),
                                                        # Production Info
                                                        dmc.Paper(
                                                            p="md",
                                                            withBorder=True,
                                                            children=[
                                                                dmc.Text("Production", fw=700, mb="sm"),
                                                                dmc.Text(
                                                                    f"Companies: {', '.join([company['name'] for company in movie_info.get('production_companies', [])])}",
                                                                    size="sm"
                                                                ),
                                                                dmc.Space(h=5),
                                                                dmc.Text(
                                                                    f"Budget: ${movie_info.get('budget', 0):,}",
                                                                    size="sm"
                                                                ),
                                                                dmc.Space(h=5),
                                                                dmc.Text(
                                                                    f"Revenue: ${movie_info.get('revenue', 0):,}",
                                                                    size="sm"
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                                # Right column
                                                dmc.Stack(
                                                    children=[
                                                        # Rating details
                                                        dmc.Paper(
                                                            p="md",
                                                            withBorder=True,
                                                            children=[
                                                                dmc.Text("Rating Details", fw=700, mb="sm"),
                                                                dmc.Group(
                                                                    children=[
                                                                        dmc.Text(f"{movie_info['vote_count']} votes"),
                                                                        dmc.Rating(
                                                                            value=movie_info['vote_average'] / 2,
                                                                            count=5,
                                                                            size="lg",
                                                                            readOnly=True
                                                                        )
                                                                    ]
                                                                ),
                                                                dmc.Space(h=5),
                                                                dmc.Text(
                                                                    f"Average Rating: {movie_info['vote_average']:.1f}/10",
                                                                    size="sm"
                                                                )
                                                            ]
                                                        ),
                                                        # Languages and Runtime
                                                        dmc.Paper(
                                                            p="md",
                                                            withBorder=True,
                                                            children=[
                                                                dmc.Text("Additional Info", fw=700, mb="sm"),
                                                                dmc.Text(
                                                                    f"Languages: {', '.join([language['english_name'] for language in movie_info.get('spoken_languages', [])])}",
                                                                    size="sm"
                                                                ),
                                                                dmc.Space(h=5),
                                                                dmc.Text(
                                                                    f"Runtime: {movie_info.get('runtime', 0)} minutes",
                                                                    size="sm"
                                                                ),
                                                                dmc.Space(h=5),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        
                                        dmc.Space(h=20),
                                        
                                        # Tags section
                                        dmc.Paper(
                                            p="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Text("Movie Tags", fw=700, mb="sm"),
                                                dmc.Group(
                                                    gap="xs",
                                                    children=[
                                                        dmc.Badge(
                                                            tag['tag'],
                                                            size="md",
                                                            variant="filled",
                                                            color="#e64980",
                                                            style={
                                                                'opacity': tag['relevance'],
                                                                'cursor': 'help'
                                                            },
                                                            rightSection=dmc.Text(
                                                                f"{tag['relevance']:.2f}",
                                                                size="xs",
                                                                span=True
                                                            )
                                                        )
                                                        for tag in sorted(
                                                            movie_info.get('tags', []),
                                                            key=lambda x: x['relevance'],
                                                            reverse=True
                                                        )
                                                    ],
                                                    style={'flexWrap': 'wrap'}
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        
                        dmc.Space(h=30),
                        
                        # Cast section
                        dmc.Title("Cast", order=2, style={'color': COLORS['text']}),
                        dmc.Space(h=10),
                        dmc.ScrollArea(
                            offsetScrollbars=True,
                            type="scroll",
                            children=dmc.SimpleGrid(
                                cols=6,
                                spacing="lg",
                                children=[
                                    dmc.Paper(
                                        p="md",
                                        radius="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Image(
                                                src=f"https://image.tmdb.org/t/p/w200{actor.get('profile_path')}" if actor.get('profile_path') else "https://via.placeholder.com/200x300",
                                                h=200,
                                                fit="cover",
                                                radius="md"
                                            ),
                                            dmc.Text(actor.get('name', 'Unknown'), fw=700),
                                            dmc.Text(actor.get('character', 'Unknown Role'), size="sm", c="dimmed"),
                                            dmc.Space(h=5),
                                            dmc.Anchor(
                                                dmc.Button(
                                                    "View Profile",
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm"
                                                ),
                                                href=f"/actor?actorID={actor.get('id')}&db_type={db_type}"
                                            )
                                        ]
                                    )
                                    for actor in movie_credits.get('cast_', [])[:12] if isinstance(actor, dict)
                                ]
                            )
                        ),
                        
                        dmc.Space(h=30),
                        
                        # Similar movies section
                        dmc.Title("Similar Movies", order=2, style={'color': COLORS['text']}),
                        dmc.Space(h=10),
                        dmc.ScrollArea(
                            offsetScrollbars=True,
                            type="scroll",
                            children=dmc.SimpleGrid(
                                cols=6,
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
                                            dmc.Text(movie['title'], fw=700),
                                            dmc.Space(h=5),
                                            dmc.Anchor(
                                                dmc.Button(
                                                    "View Details",
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm"
                                                ),
                                                href=f"/info?movieID={movie['movieId']}&db_type={db_type}"
                                            )
                                        ]
                                    )
                                    for movie in similar_movies['movies']
                                ]
                            )
                        ),
                    ]
                )
            ]
        )
        
        # Create performance metrics
        metrics = [
            f"Total Time: {query_info['query_times']['total']}",
            f"Database: {db_type.upper()}"
        ]
        
        # Create query info hover content
        hover_content = [
            dmc.Text("Query Information:", size="sm", fw=700),
            dmc.Space(h=5),
            dmc.Text("Movie Info Query:", size="sm", fw=500),
            dmc.Text(f"Time: {query_info['query_times']['movie_info']}", size="sm", c="dimmed"),
            dmc.Code(
                query_info['query_statements']['movie_info'],
                block=True,
                color="blue",
                style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
            ),
            dmc.Space(h=10),
            dmc.Text("Credits Query:", size="sm", fw=500),
            dmc.Text(f"Time: {query_info['query_times']['credits']}", size="sm", c="dimmed"),
            dmc.Code(
                query_info['query_statements']['credits'],
                block=True,
                color="blue",
                style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
            ),
            dmc.Space(h=10),
            dmc.Text("Similar Movies Query - High Score:", size="sm", fw=500),
            dmc.Text(f"Time: {query_info['query_times']['similar_movies']}", size="sm", c="dimmed"),
            dmc.Code(
                query_info['query_statements']['high_score_movies'],
                block=True,
                color="blue",
                style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
            ),
            dmc.Space(h=10),
            dmc.Text("Similar Movies Query - Movies with Companies:", size="sm", fw=500),
            dmc.Text(f"Time: {query_info['query_times']['similar_movies']}", size="sm", c="dimmed"),
            dmc.Code(
                query_info['query_statements']['movies_with_companies'],
                block=True,
                color="blue",
                style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
            ),
            dmc.Space(h=10),
            dmc.Text("Similar Movies Query - Similar Genres:", size="sm", fw=500),
            dmc.Text(f"Time: {query_info['query_times']['similar_movies']}", size="sm", c="dimmed"),
            dmc.Code(
                query_info['query_statements']['similar_genres'],
                block=True,
                color="blue",
                style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '200px'}
            ),
            dmc.Space(h=10),
            dmc.Text("Performance Summary:", size="sm", fw=500),
            dmc.Code(
                f"Movie ID: {movieID}\n"
                f"Database: {db_type}\n"
                f"Movie Info Time: {query_info['query_times']['movie_info']}\n"
                f"Credits Time: {query_info['query_times']['credits']}\n"
                f"Similar Movies Time: {query_info['query_times']['similar_movies']}\n"
                f"Total Time: {query_info['query_times']['total']}",
                block=True,
                color="green",
                style={'whiteSpace': 'pre-wrap'}
            )
        ]
        
        session.close()
        
        return movie_html, None, False, query_info, " | ".join(metrics), hover_content
        
    except Exception as e:
        logger.error(f"Error showing movie info: {str(e)}", exc_info=True)
        return html.Div(f"Error loading movie information: {str(e)}"), None, False, None, "", ""
