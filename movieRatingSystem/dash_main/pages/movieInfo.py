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
# session = Session()
dash.register_page(__name__, path='/info')

def layout(movieID=None, **other_unknown_query_strings):
    return html.Div(
        children=[
            dmc.LoadingOverlay(id='loading-overlay-movie-info',
                                overlayProps={"radius": "sm", "blur": 2},
                                zIndex=10,
                                visible=True,
            ),
            html.Button(children='hello', id='test-button', style={'display' : 'None'}),
            html.Span(id='movieID', style={'display' : 'None'}, children=movieID),
            dcc.Store(id='movie-recommend-data'),
            html.Div(id='movie-container'),
        ]
    )

@dash.callback(
    Output("movie-container", "children"),
    Output('movie-recommend-data', 'data'),
    Output('loading-overlay-movie-info', 'visible'),
    Input('test-button', 'n_clicks'),
    State('movieID', 'children'),
)
def showMovieInfo(nclicks, movieID):

    specificMovieInfo = pd.read_sql(f"SELECT * FROM specificMovie WHERE \"movieId\" = {movieID};", DATABASE_URL).to_dict('records')[0]
    specificMovieGenome = pd.read_sql(f"SELECT * FROM genome_non_materialized WHERE \"movieId\" = {movieID} ORDER BY keywordvalue DESC LIMIT 12;", DATABASE_URL).rename(columns={'keywordvalue' : 'value', 'tag' : 'label'})[['label', 'value']]
    specificMovieActors = pd.read_sql(f"SELECT * FROM actors WHERE \"movieId\" = {movieID};", DATABASE_URL)

    genomes = specificMovieGenome.head(3)['label'].to_list()

    movieHTML = html.Div(
        dmc.Center(
            children=[
                dmc.Grid(
                    children=[
                        dmc.GridCol(span=3),
                        dmc.GridCol(dmc.Title(children=f"{specificMovieInfo['title']} ({specificMovieInfo['release_date'].year})"), span=9),
                        dmc.GridCol(span=3),
                        dmc.GridCol(
                                    children=[
                                                dmc.Image(src=f"https://image.tmdb.org/t/p/original{specificMovieInfo['poster_path']}", h=350, w=280),
                                                dmc.Group(
                                                    children=[
                                                        html.A(dmc.Button("IMDB Page", leftSection=DashIconify(icon="lineicons:imdb", width=20), variant='light',), target="_blank", href='https://www.imdb.com/title/tt'+ ((7 - len(str(specificMovieInfo['imdbid']))) * '0') + str(specificMovieInfo['imdbid'])),
                                                        html.A(dmc.Button("TMDB Page", leftSection=DashIconify(icon="hugeicons:tv-02", width=20), variant='light'), target="_blank", href='https://www.themoviedb.org/movie/' + str(specificMovieInfo['tmdbid'])),
                                                    ],
                                                    style={'margin-top' : '25px'}
                                                )
                                            ],
                                    span=2),
                        dmc.GridCol(
                            children=[
                                dmc.Group(
                                    children=[
                                        dmc.Text(round(specificMovieInfo['vote_average'], 2), size='xl', c='white', style={'background-color' : 'green' if round(specificMovieInfo['vote_average'], 2) > 7 else 'orange', 'padding' : '5px'}),
                                        dmc.Flex(
                                            children=[
                                                dmc.Text(f"Ratings: {round(specificMovieInfo['vote_average'], 2)} from {int(specificMovieInfo['vote_count'])} TMDB users"),
                                                dmc.Group(
                                                    children=[
                                                        dmc.Text(f"User Ratings : "),
                                                        dmc.Rating(fractions=2, value=round(specificMovieInfo['rating'], 2), readOnly=True)
                                                    ]
                                                )
                                            ],
                                            direction='column'
                                        )
                                        
                                    ],
                                    style={'margin-bottom' : '15px'}
                                ),
                                dmc.Text(specificMovieInfo['overview']),
                                dmc.Divider(variant="solid" , style={'margin-top' : '25px'}),
                                dmc.Flex(
                                    children=[
                                        dmc.Text(f"Produced By : {specificMovieInfo['production_studios']}"),
                                        dmc.Text(f"Available in : {specificMovieInfo['languages']}"),
                                        dmc.Text(f"Genres : {specificMovieInfo['genres']}"),
                                        dmc.Group(
                                            children=[
                                                dmc.Text(f"Tags :"),
                                                dmc.Group(children=[dmc.Badge(genome['label']) for genome in specificMovieGenome.to_dict('records')]),
                                            ]
                                        ),
                                    ],
                                    direction='column'
                                ),
                                dmc.Divider(variant="solid" , style={'margin-top' : '25px'}),
                            ],
                            span=4,
                        ), 
                        dmc.GridCol(span=3),
                        dmc.GridCol(span=3),
                        dmc.GridCol(
                            children=[
                                dmc.Divider(variant="solid" , style={'margin-top' : '25px', 'margin-bottom' : '25px'}),
                                dmc.Text('Actors/Actresses', size='xl'),
                                dmc.ScrollArea(
                                    w=1300, h=280,
                                    scrollbars='x',
                                    id='actor-container',
                                    children=[
                                        dmc.Flex(
                                            children=[
                                                dmc.Flex(
                                                    children=[
                                                        dmc.Image(src=f"https://image.tmdb.org/t/p/original{actor['profile_path']}" if actor['profile_path'] else "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-4-user-grey-d8fe957375e70239d6abdd549fd7568c89281b2179b5f4470e2e12895792dfa5.svg", h=150, w=100),
                                                        dcc.Link(dmc.Text(actor['actor_name'], w=100), href=f"/actor?actorID={actor['actor_id']}"),
                                                        dmc.Text(actor['character'], w=100, size='sm'),
                                                    ],
                                                    direction='column',
                                                    h=200,
                                                ) for actor in specificMovieActors.to_dict('records')
                                            ],
                                            gap='lg'
                                        )
                                    ]
                                )
                            ],
                            span=6
                        ),
                        dmc.GridCol(span=3),
                        dmc.GridCol(span=3),
                        dcc.Loading(
                            dmc.GridCol(id='similar-movie-results',span=6),
                        )

                    ],
                )
            ]
        )
    )

    return movieHTML, genomes, False

@dash.callback(
    Output("similar-movie-results", "children"),
    Input('movie-recommend-data', 'data'),
    State('movieID', 'children'),
)
def showMovieRec(genomes, movieID):


    for x in range(len(genomes)):
        genomes[x] = f"'{genomes[x]}'"

    genomeString = f"({', '.join(genomes)})"
    similarMovies = pd.read_sql(f"SELECT k.\"movieId\", k.score, m.title, m.poster_path FROM (SELECT \"movieId\", AVG(keywordvalue) AS score FROM genome WHERE tag in {genomeString} AND \"movieId\" <> {movieID} AND keywordvalue > 0.8 GROUP BY \"movieId\" ORDER BY score DESC LIMIT 35) k JOIN movie_metadata m ON k.\"movieId\" = m.\"movieId\";", DATABASE_URL)

    movieRecsHTML = html.Div(
        children=[
                dmc.Divider(variant="solid" , style={'margin-top' : '25px', 'margin-bottom' : '25px'}),
                dmc.Text('Similar Movies', size='xl'),
                dmc.ScrollArea(
                    w=1300, h=280,
                    scrollbars='x',
                    id='actor-container',
                    children=[
                        dmc.Flex(
                            children=[
                                dmc.Flex(
                                    children=[
                                        dmc.Image(src=f"https://image.tmdb.org/t/p/original{movie['poster_path']}" if movie['poster_path'] else "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-4-user-grey-d8fe957375e70239d6abdd549fd7568c89281b2179b5f4470e2e12895792dfa5.svg", h=150, w=100),
                                        dcc.Link(dmc.Text(movie['title'], w=100), href=f"/info?movieID={movie['movieId']}"),
                                    ],
                                    direction='column',
                                    h=200,
                                ) for movie in similarMovies.to_dict('records')
                            ],
                            gap='lg'
                        )
                    ]
                )
            ]
        )


    return movieRecsHTML
