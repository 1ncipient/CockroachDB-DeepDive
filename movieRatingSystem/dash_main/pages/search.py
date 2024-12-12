from dash import Input, Output, State, dash_table, dcc, html, ALL, ctx, callback, callback_context
import dash
import plotly.express as px
import pandas as pd 
import polars as pl
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import os
from dotenv import load_dotenv
from movieRatingSystem.utils.db_utils import (
    with_db_session,
    initialize_data,
    search_movies
)
from movieRatingSystem.styles.common import COLORS, STYLES
from movieRatingSystem.logging_config import get_logger
from movieRatingSystem.utils.export_query_data import QueryExporter
from datetime import datetime, date
from time import perf_counter, sleep
from dash.exceptions import PreventUpdate
from typing import Union

ITEMS_PER_PAGE = 20
LOADING_OVERLAY_MIN_TIME = 0.3
logger = get_logger()

load_dotenv()
dash.register_page(
    __name__,
    path='/movies/',
    title='Search Movies'
)
dash._dash_renderer._set_react_version('18.2.0')

# Initialize data with error handling and fallback mechanism
genres, languages, keywords = initialize_data()

# Log the initialization results
if any([genres, languages, keywords]):
    logger.info(f"Successfully initialized data with {len(genres)} genres, {len(languages)} languages, and {len(keywords)} keywords")
else:
    logger.warning("All databases failed to provide initial data, using empty lists")

# Create empty lists if any of the data is None
genres = genres or []
languages = languages or []
keywords = keywords or []

def get_rating_color(rating: Union[float, int]) -> str:
    """Return a color based on the rating value."""
    if rating >= 8.0:
        return "rgba(39, 174, 96, 0.618)"  # Excellent
    elif rating >= 6.5:
        return "rgba(41, 128, 185, 0.618)"   # Good
    elif rating >= 5.0:
        return "rgba(230, 126, 34, 0.618)" # Average
    else:
        return "rgba(192, 57, 43, 0.618)"    # Poor

def create_movie_grid(movies, db_type):
    """Create a grid of movie cards."""
    if not movies:
        return dmc.Text("No movies found", ta="center", c="dimmed", fz="lg")
    
    return dmc.SimpleGrid(
        cols=2,
        spacing="lg",
        style={
            '@media (max-width: 600px)': {'gridTemplateColumns': 'repeat(1, 1fr)'}
        },
        children=[create_movie_card(movie, db_type) for movie in movies]
    )

def create_movie_card(movie, db_type):
    """Create a movie card with rating badge."""
    rating = movie.get('vote_average', 0)
    rating_color = get_rating_color(rating)
    
    return dmc.Paper(
        shadow="sm",
        p=0,
        radius="md",
        withBorder=True,
        style={
            'height': '100%',
            'overflow': 'hidden',
            'backgroundColor': 'white',
            'transition': 'transform 150ms ease, box-shadow 150ms ease',
            'position': 'relative',
            '&:hover': {
                'transform': 'translateY(-5px)',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
            }
        },
        children=[
            # Movie poster as background
            dmc.Image(
                src=f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "https://placehold.co/500x750?text=Not+Available",
                h=400,
                fit="cover",
                w="100%"
            ),
            # Gradient overlay
            dmc.Box(
                style={
                    'position': 'absolute',
                    'top': 0,
                    'left': 0,
                    'right': 0,
                    'bottom': 0,
                    'background': 'linear-gradient(0deg, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.6) 50%, rgba(0, 0, 0, 0.2) 100%)',
                },
                p="md",
                children=[
                    dmc.Badge(
                        f"{movie.get('vote_average', 0):.1f}",
                        style={'position': 'absolute', 'top': '1rem', 'right': '1rem', 'height': '3rem', 'width': '3rem', 'fontSize': '1rem'},
                        color=rating_color,
                        circle=True,
                    ),
                    # Movie info container
                    dmc.Stack(
                        style={
                            'position': 'absolute',
                            'top': '61.8%',
                            'bottom': '1rem',
                            'left': 0,
                            'right': 0,
                            'color': 'white'
                        },
                        px='0.7rem',
                        gap="0.5rem",
                        justify="space-around",
                        children=[
                            # Title and rating
                            dmc.Group(
                                justify="space-between",
                                align="center",
                                children=[
                                    dmc.Stack(
                                        gap=0,
                                        children=[
                                            dmc.Text(
                                                movie.get('title', 'Unknown Title'),
                                                fw=700,
                                                fz="md",
                                                style={'color': 'white'}
                                            ),
                                            dmc.Text(
                                                f"{movie.get('runtime', 0)} mins",
                                                fz="sm",
                                                c="dimmed",
                                                style={'color': 'rgba(255, 255, 255, 0.85)'}
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                            # Genres
                            dmc.Text(
                                ', '.join(movie.get('genres', [])) if isinstance(movie.get('genres'), list) else movie.get('genres', ''),
                                fz="sm",
                                style={'color': 'rgba(255, 255, 255, 0.85)'}
                            ),
                            # Year and view details
                            dmc.Group(
                                justify="space-between",
                                align="center",
                                children=[
                                    dmc.Text(
                                        movie.get('release_date').year if isinstance(movie.get('release_date'), date) else '',
                                        fz="sm",
                                        style={'color': 'rgba(255, 255, 255, 0.85)'}
                                    ),
                                    # View details button   
                                    dcc.Link(
                                        dmc.Button(
                                            "View Details",
                                            variant="filled",
                                            size="xs",
                                            color="blue",
                                            rightSection=DashIconify(
                                                icon="ic:round-arrow-forward",
                                                width=16
                                            )
                                        ),
                                        href=f"/info?movieID={movie['movieId']}&db_type={db_type}"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_database_section(title, db_name):
    """Create a section for database results with performance metrics and query info."""
    return dmc.GridCol(
        span=4,
        children=[
            dmc.Paper(
                p="md",
                shadow="sm",
                withBorder=True,
                children=[
                    dmc.Stack(
                        pos="relative",
                        children=[
                            dmc.LoadingOverlay(
                                id=f'results-loading-{db_name}',
                                visible=True,
                                overlayProps={"radius": "sm", "blur": 2},
                                zIndex=10,
                            ),
                            # Header with performance info
                            dmc.Group(
                                justify="space-between",
                                children=[
                                    dmc.Stack(
                                        gap=0,
                                        children=[
                                            dmc.Text(title, size="lg", fw=700),
                                            # Performance metrics
                                            dmc.Group(
                                                mt="xs",
                                                children=[
                                                    dmc.Text(
                                                        id=f'performance-metrics-{db_name}',
                                                        size="sm",
                                                        c="dimmed"
                                                    ),
                                                ]
                                            ),
                                        ],
                                    ),
                                    dmc.HoverCard(
                                        width=600,
                                        shadow="md",
                                        children=[
                                            dmc.HoverCardTarget(
                                                dmc.Button(
                                                    "Query Info",
                                                    variant="light",
                                                    size="sm",
                                                    leftSection=DashIconify(icon="carbon:sql-reference"),
                                                )
                                            ),
                                            dmc.HoverCardDropdown(
                                                id=f'query-info-hover-{db_name}',
                                                children=[
                                                    dmc.Code("Loading query information...", color="red")
                                                ]
                                            )
                                        ],
                                    ),
                                ]
                            ),
                            # Results section
                            html.Div(
                                id=f'movie-grid-{db_name}',
                                style={'minHeight': '200px'}
                            ),
                            # Pagination
                            dmc.Group(
                                justify="center",
                                gap="md",
                                mt="md",
                                children=[
                                    dmc.Pagination(
                                        id=f'pagination-{db_name}',
                                        total=1,
                                        value=1,
                                        style={'marginTop': '10px'}
                                    )
                                ]
                            )   
                        ]
                    )
                ]
            )
        ]
    )

def handle_db_result(result, db_name):
    """Handle database result and return appropriate output."""
    if isinstance(result, dict) and result.get('error'):
        # Database error occurred
        return (
            dmc.Alert(
                title="Database Error",
                color="red",
                children=[
                    dmc.Text(result['message'], size="sm"),
                    dmc.Text(result.get('details', ''), size="xs", c="dimmed", mt="xs")
                ]
            ),
            1,  # total pages
            False  # loading state
        )
    
    # Normal result processing
    if isinstance(result, tuple) and len(result) == 3:
        return result
    
    # Fallback for unexpected results
    return (
        dmc.Alert(
            title="Unexpected Error",
            color="red",
            children="An unexpected error occurred while processing the results."
        ),
        1,
        False
    )

layout = [
    html.Div(
        style={**STYLES['page_container'], 'maxWidth': '95%', 'margin': '0 auto'},
        children=[
            # Central Search Panel
            dmc.Stack(
                pos="relative",
                children=[
                    dmc.LoadingOverlay(
                        id="search-panel-loading",
                        visible=True,
                        overlayProps={"radius": "sm", "blur": 2},
                        zIndex=10,
                    ),
                    dmc.Paper(
                        p="md",
                        shadow="md",
                        withBorder=True,
                        style={'marginBottom': '30px'},
                        children=[
                            # Search Header
                            dmc.Text("Movie Search", size="xl", fw=700, style={'marginBottom': '20px'}),
                            
                            # Search Filters
                            dmc.Grid(
                                gutter="md",
                                children=[
                                    # Left Column - Basic Filters
                                    dmc.GridCol(
                                        span=4,
                                        children=dmc.Paper(
                                            p="md",
                                            shadow="sm",
                                            withBorder=True,
                                            children=[
                                                dmc.Text("Basic Filters", size="md", fw=500, style={'marginBottom': '10px'}),
                                                dmc.TextInput(
                                                    label="Search by Title",
                                                    placeholder="Enter movie title...",
                                                    leftSection=DashIconify(icon="ic:round-search"),
                                                    id='title-search',
                                                    style=STYLES['input']
                                                ),
                                                dmc.MultiSelect(
                                                    data=genres,
                                                    label='Genres',
                                                    placeholder="Select genres...",
                                                    id='genre-select',
                                                    searchable=True,
                                                    style=STYLES['input']
                                                ),
                                                dmc.MultiSelect(
                                                    data=languages,
                                                    label='Languages',
                                                    placeholder="Select languages...",
                                                    id='language-select',
                                                    searchable=True,
                                                    style=STYLES['input']
                                                ),
                                            ]
                                        )
                                    ),
                                    
                                    # Middle Column - Advanced Filters
                                    dmc.GridCol(
                                        span=4,
                                        children=dmc.Paper(
                                            p="md",
                                            shadow="sm",
                                            withBorder=True,
                                            children=[
                                                dmc.Text("Advanced Filters", size="md", fw=500, style={'marginBottom': '10px'}),
                                                dmc.YearPickerInput(
                                                    type="range",
                                                    label="Release Year Range",
                                                    placeholder="Select years",
                                                    id='year-range-select',
                                                    style=STYLES['input']
                                                ),
                                                dmc.Text(
                                                    "Movie Rating (0-10)",
                                                    size="sm",
                                                    fw=500,
                                                    style={'marginTop': '10px'}
                                                ),
                                                dmc.Text(
                                                    "Filter movies by their average user rating",
                                                    size="xs",
                                                    c="dimmed",
                                                    style={'marginBottom': '5px'}
                                                ),
                                                dmc.RangeSlider(
                                                    id='rating-range',
                                                    min=0,
                                                    max=10,
                                                    step=0.5,
                                                    value=[0, 10],
                                                    marks=[
                                                        {"value": i, "label": str(i)}
                                                        for i in range(0, 11, 1)
                                                    ],
                                                    minRange=0.5,
                                                    style=STYLES['input']
                                                ),
                                                dmc.Text(
                                                    "Movie Runtime (minutes)",
                                                    size="sm",
                                                    fw=500,
                                                    style={'marginTop': '20px'}
                                                ),
                                                dmc.Text(
                                                    "Filter movies by their duration",
                                                    size="xs",
                                                    c="dimmed",
                                                    style={'marginBottom': '5px'}
                                                ),
                                                dmc.RangeSlider(
                                                    id='runtime-range',
                                                    min=0,
                                                    max=240,
                                                    step=15,
                                                    value=[0, 240],
                                                    marks=[
                                                        {"value": i, "label": str(i)}
                                                        for i in range(0, 241, 30)
                                                    ],
                                                    minRange=15,
                                                    style=STYLES['input']
                                                ),
                                            ]
                                        )
                                    ),
                                    
                                    # Right Column - Tags and Sort
                                    dmc.GridCol(
                                        span=4,
                                        children=dmc.Paper(
                                            p="md",
                                            shadow="sm",
                                            withBorder=True,
                                            children=[
                                                dmc.Text("Additional Options", size="md", fw=500, style={'marginBottom': '10px'}),
                                                dmc.MultiSelect(
                                                    data=keywords,
                                                    label='Movie Keywords',
                                                    placeholder="Select keywords...",
                                                    id='type-select',
                                                    searchable=True,
                                                    style=STYLES['input']
                                                ),
                                                dmc.Switch(
                                                    id='adult-content',
                                                    label="Include Adult Content",
                                                    size="md",
                                                    style=STYLES['input']
                                                ),
                                                dmc.Select(
                                                    data=[
                                                        {"value": "popularity", "label": "Sort by Popularity"},
                                                        {"value": "rating", "label": "Sort by Rating"},
                                                        {"value": "release_date", "label": "Sort by Release Date"},
                                                        {"value": "title", "label": "Sort by Title"}
                                                    ],
                                                    label="Sort Results",
                                                    placeholder="Select sorting option...",
                                                    id='sort-by-select',
                                                    value="popularity",
                                                    style=STYLES['input']
                                                ),
                                            ]
                                        )
                                    ),
                                ]
                            ),
                            
                            # Search Button
                            dmc.Group(
                                justify="center",
                                mt="xl",
                                children=[
                                    dmc.Button(
                                        'Search Movies',
                                        id='submit-selection',
                                        variant="filled",
                                        size="md",
                                        leftSection=DashIconify(icon="ic:round-search"),
                                        style=STYLES['button']
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Results Grid with spacing between columns
            dmc.Grid(
                gutter="xl",
                style={'marginTop': '20px'},
                children=[
                    create_database_section("CockroachDB Results", "cockroach"),
                    create_database_section("PostgreSQL Results", "postgres"),
                    create_database_section("MariaDB Results", "mariadb"),
                ]
            )
        ]
    ),

    dcc.Store(id='query-info-cockroach'),
    dcc.Store(id='query-info-postgres'),
    dcc.Store(id='query-info-mariadb'),
    dcc.Store(id='current-page-cockroach', data=1),
    dcc.Store(id='current-page-postgres', data=1),
    dcc.Store(id='current-page-mariadb', data=1),
]

def update_movie_results(db_name, session, n_clicks, page, sort_by, title=None, genres=None, languages=None, 
                      years=None, rating_range=None, runtime_range=None, keywords=None, include_adult=False):
    """Generic function to update movie results for any database."""
    if not page:
        page = 1
    
    try:
        start_time = perf_counter()
        conditions = []
        

        # Process title
        if title is not None:
            conditions.append({
                'type': 'title',
                'value': title
            })
            logger.info(f"Added title filter: {title}")

        # Process genres
        if genres is not None:
            conditions.append({
                'type': 'genres',
                'value': genres
            })
            logger.info(f"Added genre filter: {genres}")

        # Process languages (using ISO codes from MultiSelect values)
        if languages is not None:
            conditions.append({
                'type': 'languages',
                'value': languages  # MultiSelect already returns ISO codes as values
            })
            logger.info(f"Added language filter (ISO codes): {languages}")

            # Process years
        if years and isinstance(years, list) and len(years) == 2 and all(years):
            try:
                year_range = [y[:4] if y else None for y in years]
                if all(year_range):  # Only add if both years are valid
                    conditions.append({
                        'type': 'years',
                        'value': (year_range[0], year_range[1])
                    })
                    logger.info(f"Added year filter: {year_range[0]} to {year_range[1]}")
            except (TypeError, IndexError) as e:
                logger.warning(f"Invalid year format: {years}. Error: {str(e)}")

        # Process rating range
        if rating_range is not None:
            conditions.append({
                'type': 'rating',
                'value': {
                    'min': rating_range[0],
                    'max': rating_range[1]
                }
            })
            logger.info(f"Added rating filter: {rating_range[0]} to {rating_range[1]}")

        # Process runtime range
        if runtime_range is not None:
            conditions.append({
                'type': 'runtime',
                'value': {
                    'min': runtime_range[0],
                    'max': runtime_range[1]
                }
            })
            logger.info(f"Added runtime filter: {runtime_range[0]} to {runtime_range[1]}")

        # Process adult content
        if include_adult is not None:
            conditions.append({
                'type': 'adult',
                'value': False
            })
            logger.info("Excluded adult content")

        # Process keywords
        if keywords is not None:
            conditions.append({
                'type': 'keywords',
                'value': keywords
            })
            logger.info(f"Added keyword filters: {keywords}")

        # Add sorting condition
        if sort_by is not None:
            conditions.append({
                'type': 'sort',
                'value': sort_by
            })
            logger.info(f"Added sorting: {sort_by}")
        # If no search has been performed yet, show default movies sorted by popularity
        else:
            conditions.append({
                'type': 'sort',
                'value': 'popularity'
            })

        # Execute search with structured conditions
        logger.info(f"Final conditions list for {db_name}: {conditions}")
        page_data = search_movies(session, conditions, page=page)
        
        # Calculate query performance
        query_time = perf_counter() - start_time
        
        # Get the SQL query statement
        query_info = {
            'query_time': f"{query_time:.3f}s",
            'query_statement': page_data.get('query_statement', 'N/A'),
            'total_results': page_data.get('total_count', 0),
            'query_explanation': page_data.get('query_explanation', 'N/A')
        }
        
        # Calculate total pages
        total_pages = (page_data.get('total_count', 0) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        # Log results
        movie_titles = [movie.get('title', 'Unknown') for movie in page_data.get('results', [])]
        logger.info(f"{db_name} results - Page {page}/{total_pages}: {', '.join(movie_titles)}")

        query_exporter = QueryExporter(output_file=f"{db_name}_query_history.json")
        query_exporter.add_query(query_info['query_statement'], query_info['query_time'], query_info['total_results'], query_info['query_explanation'])
        
        return create_movie_grid(page_data.get('results', []), db_name), total_pages, False, query_info
    except Exception as e:
        logger.error(f"Error updating {db_name} results: {str(e)}", exc_info=True)
        return [], 1, False, {'query_time': 'N/A', 'query_statement': 'Error occurred', 'total_results': 0}

# Callbacks for each database
@callback(
    [Output('movie-grid-cockroach', 'children'),
     Output('pagination-cockroach', 'total'),
     Output('query-info-cockroach', 'data'),
     Output('performance-metrics-cockroach', 'children'),
     Output('query-info-hover-cockroach', 'children'),
     Output('results-loading-cockroach', 'visible', allow_duplicate=True)],
    [Input('submit-selection', 'n_clicks'),
     Input('pagination-cockroach', 'value'),
     Input('sort-by-select', 'value')],
    [State('title-search', 'value'),
     State('genre-select', 'value'),
     State('language-select', 'value'),
     State('year-range-select', 'value'),
     State('rating-range', 'value'),
     State('runtime-range', 'value'),
     State('type-select', 'value'),
     State('adult-content', 'value')],
     prevent_initial_call='initial_duplicate',
)
@with_db_session
def update_cockroach_results(session, n_clicks, page, sort_by, title=None, genres=None, languages=None, years=None, 
                           rating_range=None, runtime_range=None, keywords=None, include_adult=False):
    """Update movie grid with paginated results for CockroachDB."""
    result = update_movie_results('cockroach', session, n_clicks, page, sort_by, title, genres, languages,
                              years, rating_range, runtime_range, keywords, include_adult)
    grid, total_pages, _, query_info = result
    
    # Create performance metrics text
    metrics = [
        f"Query Time: {query_info['query_time']}",
        f"Total Results: {query_info['total_results']}"
    ]
    
    # Create query info hover card content
    hover_content = [
        dmc.Text("SQL Query:", size="sm", fw=700),
        dmc.Code(
            query_info['query_statement'],
            block=True,
            color="blue",
            style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '400px'}
        )
    ]

    # prevent race condition of loading overlay
    if float(query_info['query_time'].rstrip('s')) < LOADING_OVERLAY_MIN_TIME:
        sleep(LOADING_OVERLAY_MIN_TIME - float(query_info['query_time'].rstrip('s')))
    
    return grid, total_pages, query_info, " | ".join(metrics), hover_content, False

@callback(
    [Output('movie-grid-postgres', 'children'),
     Output('pagination-postgres', 'total'),
     Output('query-info-postgres', 'data'),
     Output('performance-metrics-postgres', 'children'),
     Output('query-info-hover-postgres', 'children'),
     Output('results-loading-postgres', 'visible', allow_duplicate=True)],
    [Input('submit-selection', 'n_clicks'),
     Input('pagination-postgres', 'value'),
     Input('sort-by-select', 'value')],
    [State('title-search', 'value'),
     State('genre-select', 'value'),
     State('language-select', 'value'),
     State('year-range-select', 'value'),
     State('rating-range', 'value'),
     State('runtime-range', 'value'),
     State('type-select', 'value'),
     State('adult-content', 'value')],
    prevent_initial_call='initial_duplicate',
)
@with_db_session
def update_postgres_results(session, n_clicks, page, sort_by, title=None, genres=None, languages=None, years=None, 
                          rating_range=None, runtime_range=None, keywords=None, include_adult=False):
    """Update movie grid with paginated results for PostgreSQL."""
    result = update_movie_results('postgres', session, n_clicks, page, sort_by, title, genres, languages,
                              years, rating_range, runtime_range, keywords, include_adult)
    grid, total_pages, _, query_info = result
    
    # Create performance metrics text
    metrics = [
        f"Query Time: {query_info['query_time']}",
        f"Total Results: {query_info['total_results']}"
    ]
    
    # Create query info hover card content
    hover_content = [
        dmc.Text("SQL Query:", size="sm", fw=700),
        dmc.Code(
            query_info['query_statement'],
            block=True,
            color="blue",
            style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '400px'}
        )
    ]

    # prevent race condition of loading overlay
    if float(query_info['query_time'].rstrip('s')) < LOADING_OVERLAY_MIN_TIME:
        sleep(LOADING_OVERLAY_MIN_TIME - float(query_info['query_time'].rstrip('s')))
    
    return grid, total_pages, query_info, " | ".join(metrics), hover_content, False

@callback(
    [Output('movie-grid-mariadb', 'children'),
     Output('pagination-mariadb', 'total'),
     Output('query-info-mariadb', 'data'),
     Output('performance-metrics-mariadb', 'children'),
     Output('query-info-hover-mariadb', 'children'),
     Output('results-loading-mariadb', 'visible', allow_duplicate=True)],
    [Input('submit-selection', 'n_clicks'),
     Input('pagination-mariadb', 'value'),
     Input('sort-by-select', 'value')],
    [State('title-search', 'value'),
     State('genre-select', 'value'),
     State('language-select', 'value'),
     State('year-range-select', 'value'),
     State('rating-range', 'value'),
     State('runtime-range', 'value'),
     State('type-select', 'value'),
     State('adult-content', 'value')],
    prevent_initial_call='initial_duplicate',
)
@with_db_session
def update_mariadb_results(session, n_clicks, page, sort_by, title=None, genres=None, languages=None, years=None, 
                          rating_range=None, runtime_range=None, keywords=None, include_adult=False):
    """Update movie grid with paginated results for MariaDB."""
    result = update_movie_results('mariadb', session, n_clicks, page, sort_by, title, genres, languages,
                              years, rating_range, runtime_range, keywords, include_adult)
    grid, total_pages, _, query_info = result
    
    # Create performance metrics text
    metrics = [
        f"Query Time: {query_info['query_time']}",
        f"Total Results: {query_info['total_results']}"
    ]
    
    # Create query info hover card content
    hover_content = [
        dmc.Text("SQL Query:", size="sm", fw=700),
        dmc.Code(
            query_info['query_statement'],
            block=True,
            color="blue",
            style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'maxHeight': '400px'}
        )
    ]
    
    # prevent race condition of loading overlay
    if float(query_info['query_time'].rstrip('s')) < LOADING_OVERLAY_MIN_TIME:
        sleep(LOADING_OVERLAY_MIN_TIME - float(query_info['query_time'].rstrip('s')))
    
    return grid, total_pages, query_info, " | ".join(metrics), hover_content, False

# Add loading state callbacks
@callback(
    [Output("search-panel-loading", "visible", allow_duplicate=True),
     Output('results-loading-cockroach', 'visible', allow_duplicate=True),
     Output('results-loading-postgres', 'visible', allow_duplicate=True),
     Output('results-loading-mariadb', 'visible', allow_duplicate=True),
     Output("current-page-cockroach", "data"),
     Output("current-page-postgres", "data"),
     Output("current-page-mariadb", "data"),],
    [Input("submit-selection", "n_clicks"),
     Input("sort-by-select", "value"),
     Input("pagination-cockroach", "value"),
     Input("pagination-postgres", "value"),
     Input("pagination-mariadb", "value")],
    [State("current-page-cockroach", "data"),
     State("current-page-postgres", "data"),
     State("current-page-mariadb", "data"),
     State('results-loading-cockroach', 'visible'),
     State('results-loading-postgres', 'visible'),
     State('results-loading-mariadb', 'visible')],
    prevent_initial_call=True
)
def show_search_loading(n_clicks, sort_by, page_cockroach, page_postgres, page_mariadb, stored_page_cockroach, 
                        stored_page_postgres, stored_page_mariadb, is_loading_cockroach, is_loading_postgres, is_loading_mariadb):
    """Show loading overlay when search is triggered."""

    ctx = callback_context
    if not ctx.triggered:
        trigger_id = None
    else:
        # Get the ID of the triggering input
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Show all loading overlay
    if trigger_id == "submit-selection" or trigger_id == "sort-by-select":
        return True, True, True, True, page_cockroach, page_postgres, page_mariadb

    # Check which page has changed and only disable that section
    if page_cockroach != stored_page_cockroach:
        return True, True, is_loading_postgres, is_loading_mariadb, page_cockroach, page_postgres, page_mariadb
    if page_postgres != stored_page_postgres:
        return True, is_loading_cockroach, True, is_loading_mariadb, page_cockroach, page_postgres, page_mariadb
    if page_mariadb != stored_page_mariadb:
        return True, is_loading_cockroach, is_loading_postgres, True, page_cockroach, page_postgres, page_mariadb

    # Default behavior if no recognized trigger
    return False, is_loading_cockroach, is_loading_postgres, is_loading_mariadb, stored_page_cockroach, stored_page_postgres, stored_page_mariadb

@callback(
    Output("search-panel-loading", "visible", allow_duplicate=True),
    [Input('results-loading-cockroach', 'visible'),
     Input('results-loading-postgres', 'visible'),
     Input('results-loading-mariadb', 'visible')],
    prevent_initial_call=True
)
def hide_search_loading(*results):
    """Hide search panel loading when all results are loaded."""
    if not any(results):
        return False
    return True

