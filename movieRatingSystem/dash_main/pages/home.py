"""Creates Home page that is viewing right after landing page."""
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from movieRatingSystem.styles.common import STYLES, COLORS
from movieRatingSystem.logging_config import get_logger

dash.register_page(
    __name__,
    path='/home',  # Set as root path to make it the default/home page
    title='Home'
)

hero_section = html.Div(
    style={
        'height': 'calc(100vh - 70px)',  # Subtract navbar height
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'backgroundImage': 'linear-gradient(rgba(20, 20, 20, 0.8), rgba(20, 20, 20, 0.8)), url(https://image.tmdb.org/t/p/original/628Dep6AxEtDxjZoGP78TsOxYbK.jpg)',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'color': COLORS['text']
    },
    children=[
        dmc.Container(
            size="lg",
            style={'textAlign': 'center'},
            children=[
                dmc.Title(
                    "Discover Your Next Favorite Movie",
                    order=1,
                    style={
                        'fontSize': '48px',
                        'marginBottom': '24px',
                        'color': COLORS['surface'],
                        'textShadow': '0 2px 4px rgba(0,0,0,0.8)'
                    }
                ),
                dmc.Text(
                    "Explore thousands of movies, find similar recommendations, and track your favorites.",
                    size="xl",
                    c="dimmed",
                    style={'marginBottom': '48px', 'maxWidth': '800px', 'margin': '0 auto 48px'}
                ),
                dmc.Group(
                    justify="center",
                    gap="xl",
                    children=[
                        dcc.Link(
                            dmc.Button(
                                "Start Exploring",
                                size="lg",
                                radius="md",
                                leftSection=DashIconify(icon="ph:magnifying-glass-bold"),
                                style={'backgroundColor': COLORS['primary']}
                            ),
                            href="/movies/",
                            refresh=True
                        ),
                        dcc.Link(
                            dmc.Button(
                                "Browse Movies",
                                size="lg",
                                radius="md",
                                variant="outline",
                                leftSection=DashIconify(icon="ph:film-slate-bold")
                            ),
                            href="/movies/",
                            refresh=True
                        ),
                    ]
                )
            ]
        )
    ]
)

features_section = dmc.Container(
    size="lg",
    py="xl",
    children=[
        dmc.SimpleGrid(
            cols=3,
            spacing="xl",
            style={
                '@media (max-width: 992px)': {'gridTemplateColumns': 'repeat(2, 1fr)'},
                '@media (max-width: 768px)': {'gridTemplateColumns': 'repeat(1, 1fr)'}
            },
            children=[
                dmc.Paper(
                    radius="md",
                    withBorder=True,
                    p="xl",
                    style={'backgroundColor': COLORS['surface']},
                    children=[
                        DashIconify(
                            icon="ph:magnifying-glass-bold",
                            width=32,
                            color=COLORS['primary']
                        ),
                        dmc.Text(
                            "Smart Search",
                            fw=700,
                            size="lg",
                            mt="md",
                            c=COLORS['text']
                        ),
                        dmc.Text(
                            "Find movies by genre, keywords, year, and more.",
                            size="sm",
                            mt="sm",
                            c="dimmed"
                        ),
                    ],
                ),
                dmc.Paper(
                    radius="md",
                    withBorder=True,
                    p="xl",
                    style={'backgroundColor': COLORS['surface']},
                    children=[
                        DashIconify(
                            icon="ph:star-bold",
                            width=32,
                            color=COLORS['primary']
                        ),
                        dmc.Text(
                            "Ratings & Reviews",
                            fw=700,
                            size="lg",
                            mt="md",
                            c=COLORS['text']
                        ),
                        dmc.Text(
                            "See what others think and like.",
                            size="sm",
                            mt="sm",
                            c="dimmed"
                        ),
                    ],
                ),
                dmc.Paper(
                    radius="md",
                    withBorder=True,
                    p="xl",
                    style={'backgroundColor': COLORS['surface']},
                    children=[
                        DashIconify(
                            icon="ph:lightning-bold",
                            width=32,
                            color=COLORS['primary']
                        ),
                        dmc.Text(
                            "Smart Recommendations",
                            fw=700,
                            size="lg",
                            mt="md",
                            c=COLORS['text']
                        ),
                        dmc.Text(
                            "Get personalized movie suggestions based on your taste.",
                            size="sm",
                            mt="sm",
                            c="dimmed"
                        ),
                    ],
                ),
            ],
        ),
    ],
)

layout = html.Div(
    style={'backgroundColor': COLORS['background']},
    children=[
        hero_section,
        features_section,
    ],
)
