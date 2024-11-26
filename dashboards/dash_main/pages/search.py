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

genres = pd.read_sql("SELECT DISTINCT genres FROM genres;", DATABASE_URL)['genres'].to_list()

languages = pd.read_sql("SELECT DISTINCT l.language AS label, l.\"language_code\" AS value FROM languages_offered l WHERE l.\"language_code\" IS NOT NULL AND l.language IS NOT NULL;", DATABASE_URL).to_dict('records')

keywords = pd.read_sql("SELECT DISTINCT CAST(\"tagId\" AS STRING) AS value, tag AS label FROM genome_tags WHERE \"tagId\" IS NOT NULL AND tag IS NOT NULL;", DATABASE_URL).to_dict('records')

defaultData = pd.read_sql("SELECT \"movieId\", MIN(title) AS title, MIN(adult) AS adult, ROUND(AVG(vote_average),2) AS vote_average, MIN(release_date) AS release_date, string_agg(DISTINCT production_studio, ', ') AS production_studios, string_agg(DISTINCT language, ', ') AS languages, string_agg(DISTINCT genres, ', ') AS genres, ROUND(AVG(rating),2) * 2 as rating FROM searchTableRaw GROUP BY \"movieId\" ORDER BY title;", DATABASE_URL)

layout = [
    dmc.Grid(
        children=[
            dmc.GridCol(span=3),
            dmc.GridCol(children=[
                dmc.Group(
                    children=[
                        dmc.MultiSelect(data=keywords, label='Type Movie / Keywords', id='type-select', searchable=True, w=750),
                        dmc.MultiSelect(data=genres, label='Select Genre', id='genre-select', searchable=True,  w=500),
                        dmc.MultiSelect(data=languages, label='Select Language', id='language-select', searchable=True, w=500),
                        dmc.YearPickerInput(
                            type="range",
                            label="Pick dates range",
                            placeholder="Pick dates range",
                            id='year-range-select',
                        ),
                        dmc.Stack(
                            children=[
                                html.Span(),
                                dmc.Button('Submit Query', id='submit-selection', style={'margin-top' : '10px'}),
                            ]
                        )
                    ],
                    className='m-4'
                ),
                dag.AgGrid(
                    id='search-results',
                    defaultColDef={
                        "sortable": True,
                        "resizable": True,
                        "filter" : True,
                        "cellRenderer": "markdown",
                    },
                    dashGridOptions={
                        "alwaysMultiSort": True,
                        "suppressFieldDotNotation": True,
                        "pagination": True, 
                        "paginationAutoPageSize": True
                    },
                    columnSize='responsiveSizeToFit',
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
            ],
            span=6),
            dmc.GridCol(span=3),
        ]
    ),

]

# Right now it only considers 
@dash.callback(
    Output("search-results", "columnDefs"),
    Output("search-results", "rowData"),
    Input('submit-selection', 'n_clicks'),
    State('type-select', 'value'),
    State('genre-select', 'value'),
    State('language-select', 'value'),
    State('year-range-select', 'value'),
)
def update_graph(nClicks, keywords, genre, language, years):

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
        conditionalStatement.append(f"genres in {genreCondition}")

    # Check if user inputted a value for language
    if language is not None:

        # Set conditional flag to true
        conditionalExists = True
        # Add quotation marks for each element
        for x in range(len(language)):
            language[x] = f"'{language[x]}'"

        languageCondition = f"({', '.join(language)})"
        conditionalStatement.append(f"\"language_code\" in {languageCondition}")

    # Check if user inputted a value for language
    if years is not None:

        # Set conditional flag to true
        conditionalExists = True
        # Add quotation marks for each element
        for x in range(len(years)):
            years[x] = years[x][:4]

        conditionalStatement.append(f"EXTRACT(YEAR FROM release_date) BETWEEN {years[0]} AND {years[1]}")

    # Check if user selected a keyword
    if keywords is not None:
        
        # Set conditional flag to true
        conditionalExists = True
        
        keyStatements = []
        orderStatements = []
        for key in keywords:
            keyStatements.append(f"CAST(relevances->>'{key}' AS FLOAT) > 0.7")
            orderStatements.append(f"CAST(relevances->>'{key}' AS FLOAT) DESC")

        conditionalStatement.append(f"({' OR '.join(keyStatements)})")
        orderStatements =  f"ORDER BY {', '.join(orderStatements)}"

    # Append WHERE if there is any input otherwise don't include it
    if conditionalExists:
        conditionalSentence = f'WHERE {" AND ".join(conditionalStatement)}'

        # Run SQL and save it into a dataframe

        tableStatement = f"""
        SELECT
            "movieId", 
            MIN(title) AS title, 
            MIN(adult) AS adult, 
            ROUND(AVG(vote_average),2) AS vote_average, 
            MIN(release_date) AS release_date, 
            string_agg(DISTINCT production_studio, ', ') AS production_studios,
            string_agg(DISTINCT language, ', ') AS languages,
            string_agg(DISTINCT genres, ', ') AS genres,
            ROUND(AVG(rating), 2) * 2 as rating
        FROM searchTableRaw
        {conditionalSentence}
        GROUP BY "movieId" {', relevances' if orderStatements else None}
        {orderStatements if orderStatements else "ORDER BY title"}
        LIMIT 500;
        """
        print(tableStatement)
        resultDF = pd.read_sql(tableStatement, DATABASE_URL)

    else:
        resultDF = defaultData

    resultDF['movieId'] = resultDF['movieId'].apply(str)
    resultDF['Movie Title'] = '[' + resultDF['title'] + ']' + '(/movies/info?movieID=' + resultDF['movieId'] + ')'
    resultDF = resultDF.drop(['title', 'movieId'], axis=1)

    columnDefs = [
        {"headerName": col, "field": col}
        for col in resultDF.columns
    ]
    columnDefs.pop()
    columnDefs.insert(0, {'headerName' : 'Movie Title', 'field' : 'Movie Title' , "linkTarget":"_blank"})

    fileData = resultDF.to_dict("records")

    # Return the data into the AG Grid Table
    return columnDefs, fileData
