"""Common styles for the movie rating system."""

# Color scheme
COLORS = {
    'primary': '#2563eb',     # Modern Blue
    'secondary': '#1d4ed8',   # Darker Blue
    'accent': '#3b82f6',      # Light Blue
    'background': '#f8fafc',  # Very Light Gray
    'surface': '#ffffff',     # White
    'text': '#1e293b',        # Dark Blue Gray
    'light_text': '#64748b',  # Medium Blue Gray
    'white': '#ffffff',
    'success': '#22c55e',     # Green
    'warning': '#f59e0b',     # Amber
    'error': '#ef4444',       # Red
    'hover': '#f1f5f9',       # Light Gray Blue
}

# Common styles
STYLES = {
    'page_container': {
        'padding': '20px',
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'color': COLORS['text']
    },
    'card': {
        'backgroundColor': COLORS['surface'],
        'borderRadius': '8px',
        'padding': '20px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'marginBottom': '20px',
        'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
        'border': '1px solid #e2e8f0',
        '&:hover': {
            'transform': 'translateY(-2px)',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }
    },
    'title': {
        'color': COLORS['text'],
        'marginBottom': '20px',
        'fontSize': '32px',
        'fontWeight': 'bold',
        'letterSpacing': '-0.5px'
    },
    'subtitle': {
        'color': COLORS['text'],
        'marginBottom': '15px',
        'fontSize': '24px',
        'fontWeight': 'bold',
        'letterSpacing': '-0.3px'
    },
    'text': {
        'color': COLORS['light_text'],
        'fontSize': '14px',
        'lineHeight': '1.6',
        'letterSpacing': '0.2px'
    },
    'link': {
        'color': COLORS['primary'],
        'textDecoration': 'none',
        'transition': 'color 0.2s ease',
        '&:hover': {
            'color': COLORS['secondary']
        }
    },
    'button': {
        'backgroundColor': COLORS['primary'],
        'color': COLORS['white'],
        'padding': '12px 24px',
        'borderRadius': '6px',
        'border': 'none',
        'cursor': 'pointer',
        'fontSize': '14px',
        'fontWeight': '500',
        'letterSpacing': '0.5px',
        'transition': 'all 0.2s ease',
        '&:hover': {
            'backgroundColor': COLORS['secondary'],
            'transform': 'translateY(-2px)'
        }
    },
    'input': {
        'width': '100%',
        'padding': '12px',
        'borderRadius': '6px',
        'border': '1px solid #e2e8f0',
        'backgroundColor': COLORS['surface'],
        'color': COLORS['text'],
        'marginBottom': '15px',
        'transition': 'all 0.2s ease',
        '&:focus': {
            'borderColor': COLORS['primary'],
            'outline': 'none',
            'boxShadow': f'0 0 0 3px {COLORS["primary"]}15'
        }
    },
    'grid': {
        'display': 'grid',
        'gridGap': '24px',
        'padding': '20px'
    },
    'flex_center': {
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'gap': '12px'
    },
    'movie_card': {
        'width': '200px',
        'backgroundColor': COLORS['surface'],
        'borderRadius': '8px',
        'overflow': 'hidden',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'transition': 'all 0.3s ease',
        'border': '1px solid #e2e8f0',
        '&:hover': {
            'transform': 'translateY(-5px)',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'cursor': 'pointer'
        }
    },
    'movie_image': {
        'width': '100%',
        'height': '300px',
        'objectFit': 'cover',
        'transition': 'transform 0.3s ease',
        '&:hover': {
            'transform': 'scale(1.05)'
        }
    },
    'movie_info': {
        'padding': '15px',
        'backgroundColor': COLORS['surface']
    },
    'rating_badge': {
        'display': 'inline-block',
        'padding': '6px 12px',
        'borderRadius': '6px',
        'fontWeight': 'bold',
        'fontSize': '16px',
        'letterSpacing': '0.5px',
        'color': COLORS['white'],
        'boxShadow': '0 1px 2px rgba(0,0,0,0.1)'
    },
    'search_container': {
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '40px 20px'
    },
    'search_filters': {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
        'gap': '24px',
        'marginBottom': '40px',
        'backgroundColor': COLORS['surface'],
        'padding': '24px',
        'borderRadius': '8px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'border': '1px solid #e2e8f0'
    }
}

# Rating badge colors
def get_rating_color(rating):
    """Return color based on rating value."""
    if rating >= 8:
        return COLORS['success']
    elif rating >= 6:
        return COLORS['warning']
    else:
        return COLORS['error']
