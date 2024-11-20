from dash import Input, Output, State, dash_table, dcc, html, ALL, ctx
import dash
import plotly.express as px
import pandas as pd 
import polars as pl
import dash_ag_grid as dag
import dash_mantine_components as dmc
import os
from dotenv import load_dotenv

load_dotenv()

dash.register_page(__name__)
dash._dash_renderer._set_react_version('18.2.0')

DATABASE_URL = os.getenv('DATABASE_URL')

genres = pd.read_sql("SELECT DISTINCT genre_id, genre_name FROM public.movie_metadata", DATABASE_URL).rename(columns={'genre_id' : 'value', 'genre_name' : 'label'})
genres = genres[genres['value'].notnull()].to_dict("records")


isoNames = pd.read_csv('iso_639-1.csv')[['name', '639-1']]
languages = pd.read_sql("SELECT DISTINCT iso_639_1 FROM public.movie_metadata", DATABASE_URL).rename(columns={'genre_id' : 'value', 'genre_name' : 'label'})
languages = languages.merge(isoNames, left_on='iso_639_1', right_on='639-1').rename(columns={'iso_639_1' : 'value', 'name' : 'label'}).drop('639-1', axis=1).dropna().to_dict("records")

layout = [
    dmc.Group(
        children=[
            dmc.TextInput(label='Type Movie / Keywords', id='type-select', w=750),
            dmc.MultiSelect(data=genres, label='Select Genre', id='genre-select', searchable=True,  w=500),
            dmc.MultiSelect(data=languages, label='Select Language', id='language-select', searchable=True, w=500),
            dmc.YearPickerInput(
                type="range",
                label="Pick dates range",
                placeholder="Pick dates range",
                id='year-range-select',
            ),
            dmc.Button('Submit Query', id='submit-selection'),
        ],
        className='m-4'
    ),
    dag.AgGrid(
        id='search-results',
        defaultColDef={
            "sortable": True,
            "resizable": True,
        },
        dashGridOptions={
            "alwaysMultiSort": True,
            "suppressFieldDotNotation": True,
        },
        getRowStyle={
            "styleConditions": [
                {
                    "condition": "params.rowIndex % 2 !== 0",
                    "style": {
                        "backgroundColor": "rgb(220, 220, 220)"
                    },
                },
            ]
        },
    ),   
]

# Right now it only considers 
@dash.callback(
    Output("search-results", "columnDefs"),
    Output("search-results", "rowData"),
    Input('submit-selection', 'n_clicks'),
    State('genre-select', 'value'),
    State('language-select', 'value'),
    State('year-range-select', 'value'),
)
def update_graph(nClicks, genre, language, years):

    conditionalExists = False
    conditionalStatement = []
    conditionalSentence = ''

    # Check if user inputted a value for genre
    if genre is not None:

        # Set conditional flag to true
        conditionalExists = True
        # Add quotation marks for each element
        for x in range(len(genre)):
            genre[x] = f"'{genre[x]}'"

        genreCondition = f"({', '.join(genre)})"
        conditionalStatement.append(f"genre_id in {genreCondition}")

    # Check if user inputted a value for language
    if language is not None:

        # Set conditional flag to true
        conditionalExists = True
        # Add quotation marks for each element
        for x in range(len(language)):
            language[x] = f"'{language[x]}'"

        languageCondition = f"({', '.join(language)})"
        conditionalStatement.append(f"iso_639_1 in {languageCondition}")

    # Check if user inputted a value for language
    if years is not None:

        # Set conditional flag to true
        conditionalExists = True
        # Add quotation marks for each element
        for x in range(len(years)):
            years[x] = years[x][:4]

        yearCondition = f"({', '.join(years)})"
        conditionalStatement.append(f"EXTRACT(YEAR FROM release_date) BETWEEN {years[0]} AND {years[1]}")

    # Append WHERE if there is any input otherwise don't include it
    if conditionalExists:
        conditionalSentence = f'WHERE {" AND ".join(conditionalStatement)}'

    # Run SQL and save it into a dataframe

    tableStatement = f"""
    SELECT 
        DISTINCT movie_id,
        string_agg(DISTINCT genre_name, ', ') AS genres,
        movie_title,
        release_date,
        is_adult,
        string_agg(DISTINCT production_studio, ', ') AS production_studios,
        string_agg(DISTINCT language_offered, ', ') AS languages_offered
    FROM public.movie_metadata
    {conditionalSentence}
    GROUP BY movie_id, movie_title, release_date, is_adult
    LIMIT 15;
    """

    resultDF = pd.read_sql(tableStatement, DATABASE_URL)

    columnDefs = [
        {"headerName": col, "field": col}
        for col in resultDF.columns
    ]

    fileData = resultDF.to_dict("records")

    # Return the data into the AG Grid Table
    return columnDefs, fileData
