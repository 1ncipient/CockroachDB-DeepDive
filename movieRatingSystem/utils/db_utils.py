from functools import wraps
from movieRatingSystem.config.database import db_config
from movieRatingSystem.utils.query_builder import MovieQueryBuilder
from movieRatingSystem.models.movie_models import MovieMetadata, Movies, Credits, Links, Ratings, GenomeScores, GenomeTags
from sqlalchemy import func, and_, or_, Integer, Float, String, text, select, exists, cast
from sqlalchemy.dialects.postgresql import JSONB
from movieRatingSystem.logging_config import get_logger
from movieRatingSystem.utils.language_utils import create_language_options
from datetime import date
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import pandas as pd
import random
logger = get_logger()

def handle_db_error(db_name: str, error: Exception) -> dict:
    """Handle database errors and return appropriate response."""
    error_msg = f"Database error in {db_name}: {str(error)}"
    logger.error(error_msg, exc_info=True)
    
    return {
        'error': True,
        'message': f"Connection to {db_name} failed. Please try again later.",
        'details': str(error) if isinstance(error, (SQLAlchemyError, OperationalError)) else "Internal error"
    }

def with_db_session(func):
    """Decorator to handle database session management."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the database name from the function name
        db_name = None
        if 'cockroach' in func.__name__:
            db_name = 'cockroach'
        elif 'postgres' in func.__name__:
            db_name = 'postgres'
        elif 'mariadb' in func.__name__:
            db_name = 'mariadb'
        else:
            db_name = kwargs.pop('db_name', 'cockroach')  # Default to CockroachDB
        
        try:
            session = db_config.create_session(db_name)
        except Exception as e:
            return handle_db_error(db_name, e)
            
        try:
            # Add session to args if the function expects it
            if 'session' in func.__code__.co_varnames:
                result = func(session, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            return handle_db_error(db_name, e)
        finally:
            session.close()
    return wrapper

def initialize_data(db_name='cockroach'):
    """Initialize data for dropdowns with error handling and fallback to other databases."""
    available_dbs = ['cockroach', 'postgres', 'mariadb']
    
    # Try the specified database first
    if db_name in available_dbs:
        available_dbs.remove(db_name)
        available_dbs.insert(0, db_name)
    
    for db in available_dbs:
        try:
            session = db_config.create_session(db)
            try:
                genres = get_all_genres(session)
                languages = get_all_languages(session)
                keywords = get_all_keywords(session)
                
                if all([genres, languages, keywords]):  # Check if we got data from all queries
                    logger.info(f"Successfully initialized data from {db} database")
                    return genres, languages, keywords
                else:
                    logger.warning(f"Incomplete data from {db} database, trying next database")
            except Exception as e:
                logger.error(f"Error initializing data from {db}: {str(e)}", exc_info=True)
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to connect to {db}: {str(e)}", exc_info=True)
    
    # If all databases fail, return empty lists
    logger.error("All databases failed to initialize data, returning empty lists")
    return [], [], []

def get_all_genres(session):
    """Get list of all unique genres."""
    try:
        query = (
            session.query(func.unnest(Movies.genres).label('genre'))
            .distinct()
            .order_by('genre')
        )
        results = query.all()
        return [r[0] for r in results]
    except Exception as e:
        logger.error(f"Error in get_all_genres: {str(e)}", exc_info=True)
        raise

def get_all_languages(session):
    """Get list of all unique languages."""
    try:
        query = (
            session.query(MovieMetadata.original_language)
            .distinct()
            .filter(MovieMetadata.original_language.isnot(None))
            .order_by(MovieMetadata.original_language)
        )
        results = query.all()
        iso_codes = [r[0] for r in results if r[0]]  # Get non-empty ISO codes
        return create_language_options(iso_codes)
        
    except Exception as e:
        logger.error(f"Error in get_all_languages: {str(e)}", exc_info=True)
        raise

def get_all_keywords(session):
    """Get list of all genome tags (keywords)."""
    try:
        query = (
            session.query(GenomeTags.tag)
            .order_by(GenomeTags.tag)
        )
        results = query.all()
        return [r[0] for r in results]
    except Exception as e:
        logger.error(f"Error in get_all_keywords: {str(e)}", exc_info=True)
        raise

def get_movie_by_id(session, movie_id):
    """Get movie details by ID using MovieQueryBuilder."""
    try:
        # Get basic movie info
        builder = MovieQueryBuilder(session)
        result = (
            builder.base_info_query()
            .filter_by_movie_id(movie_id)
            .paginate(page=1, items_per_page=1)
        )
        
        if not result['results']:
            return None
            
        movie_info = result['results'][0]
        movie_info['movie_query_statement'] = result['query_statement']
        
        # Get genome tags with relevance scores
        # First get the movie's genome scores
        genome_scores = (
            session.query(GenomeScores.relevances)
            .filter(GenomeScores.movieId == movie_id)
            .first()
        )
        
        if genome_scores and genome_scores.relevances:
            # Convert the relevances to a pandas Series and get top 20
            relevances_series = pd.Series(genome_scores.relevances)
            top_20_tags = relevances_series.nlargest(20)
            
            # Get the tag names for the top 20 tag IDs
            tag_names_query = (
                session.query(GenomeTags.tagId, GenomeTags.tag)
                .filter(GenomeTags.tagId.in_([int(k) for k in top_20_tags.index]))
            )
            movie_info['top_20_tags_statement'] = str(tag_names_query.statement.compile(compile_kwargs={"literal_binds": True}))
            tag_names = tag_names_query.all()
            
            # Create a dict for quick tag ID to name lookup
            tag_dict = {str(tag_id): tag for tag_id, tag in tag_names}
            
            # Create the final tags list
            tags_with_scores = [
                {
                    'tag': tag_dict[tag_id],
                    'relevance': float(score)
                }
                for tag_id, score in top_20_tags.items()
                if tag_id in tag_dict
            ]
            
            movie_info['tags'] = tags_with_scores
        else:
            movie_info['tags'] = []
        
        return movie_info
    except Exception as e:
        logger.error(f"Error in get_movie_by_id: {str(e)}", exc_info=True)
        raise

def get_movie_credits(session, movie_id):
    """Get movie credits."""
    try:
        query = (
            session.query(Credits)
            .filter(Credits.movieId == movie_id)
        )
        credits_query_statement = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        result = query.first()
        if result:
            # Convert SQLAlchemy model to dictionary
            return {
                'movieId': result.movieId,
                'cast_': result.cast_,
                'crew': result.crew,
                'credits_query_statement': credits_query_statement
            }
        return None
    except Exception as e:
        logger.error(f"Error in get_movie_credits: {str(e)}", exc_info=True)
        raise

def get_movie_links(session, movie_id):
    """Get movie links."""
    try:
        query = (
            session.query(Links)
            .filter(Links.movieId == movie_id)
        )
        result = query.first()
        return dict(result._mapping) if result else None
    except Exception as e:
        logger.error(f"Error in get_movie_links: {str(e)}", exc_info=True)
        raise

def get_movie_ratings(session, movie_id):
    """Get movie ratings."""
    try:
        query = (
            session.query(Ratings)
            .filter(Ratings.movieId == movie_id)
            .order_by(Ratings.timestamp.desc())
        )
        results = query.all()
        return [dict(r._mapping) for r in results]
    except Exception as e:
        logger.error(f"Error in get_movie_ratings: {str(e)}", exc_info=True)
        raise

def get_movie_genome_scores(session, movie_id):
    """Get movie genome scores."""
    try:
        query = (
            session.query(
                GenomeScores,
                GenomeTags.tag
            )
            .join(GenomeTags, GenomeTags.tagId == func.cast(func.jsonb_object_keys(GenomeScores.relevances), Integer))
            .filter(GenomeScores.movieId == movie_id)
            .order_by(func.cast(func.jsonb_extract_path_text(GenomeScores.relevances, func.jsonb_object_keys(GenomeScores.relevances)), Float).desc())
            .limit(10)
        )
        results = query.all()
        return [dict(r._mapping) for r in results]
    except Exception as e:
        logger.error(f"Error in get_movie_genome_scores: {str(e)}", exc_info=True)
        raise

def search_movies(session, conditions=None, page=1, items_per_page=20):
    """Search movies using the MovieQueryBuilder."""
    try:
        # Parse conditions into individual parameters
        params = parse_search_conditions(conditions)
        logger.info(f"Parsed search parameters: {params}")

        query_builder = MovieQueryBuilder(session)
        query = query_builder.base_search_query()
        
        # Apply filters based on parsed parameters
        query = (
            query
            .filter_by_title(params['title'])
            .filter_by_genres(params['genres'])
            .filter_by_languages(params['languages'])
            .filter_by_rating_range(*(params['rating_range'] or (0, 10)))
            .filter_by_runtime_range(*(params['runtime_range'] or (0, 240)))
            .filter_by_adult_content(params['include_adult'])
            .filter_by_keywords(params['keywords'])
            .filter_by_years(params['years'])
            .apply_sorting(params.get('sort_by'))
        )
        
        # Get paginated results
        result = query.paginate(page=page, items_per_page=items_per_page)
        
        return result
    except Exception as e:
        logger.error(f"Error in search_movies: {str(e)}", exc_info=True)
        raise

def parse_search_conditions(conditions):
    """Parse structured search conditions into parameter dictionary."""
    params = {
        'title': None,
        'genres': None,
        'languages': None,
        'rating_range': None,
        'runtime_range': None,
        'adult': False,
        'keywords': None,
        'years': None,
        'include_adult': True,
        'sort_by': None
    }
    
    if not conditions:
        return params
    
    for condition in conditions:
        condition_type = condition.get('type')
        value = condition.get('value')
        
        if condition_type == 'title':
            params['title'] = value
        elif condition_type == 'genres':
            params['genres'] = value
        elif condition_type == 'languages':
            params['languages'] = value
        elif condition_type == 'rating':
            params['rating_range'] = (value['min'], value['max'])
        elif condition_type == 'runtime':
            params['runtime_range'] = (value['min'], value['max'])
        elif condition_type == 'adult':
            params['include_adult'] = value
        elif condition_type == 'keywords':
            params['keywords'] = value
        elif condition_type == 'years':
            params['years'] = value
        elif condition_type == 'sort':
            params['sort_by'] = value
    
    logger.info(f"Parsed parameters: {params}")
    return params
    
def get_similar_movies(session, movie_id, limit=6):
    """Get similar movies based on genome tags, production companies, and genres."""
    try:
        # Get base movie info
        base_movie = (
            session.query(Movies.genres, MovieMetadata.production_companies)
            .join(MovieMetadata, Movies.movieId == MovieMetadata.movieId)
            .filter(Movies.movieId == movie_id)
            .first()
        )
        
        if not base_movie:
            return []

        # Similar Movies Approach 1: Similar movies by genome tags
        base_genome = (
            session.query(GenomeScores.relevances)
            .filter(GenomeScores.movieId == movie_id)
            .first()
        )
        
        results = []
        high_score_movies_query_statement = "N/A"
        similar_genres_query_statement = "N/A"
        movies_with_companies_query_statement = "N/A"   
        
        if base_genome and base_genome.relevances:
            # Get top 5 tags
            top_tags = sorted(
                [(k, float(v)) for k, v in base_genome.relevances.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Get movies with high scores for these tags
            high_score_movies_query = (
                session.query(
                    MovieMetadata.movieId,
                    MovieMetadata.title,
                    MovieMetadata.poster_path,
                    MovieMetadata.vote_average,
                    MovieMetadata.popularity,
                    Movies.genres,
                    func.avg(Ratings.rating).label('user_rating'),
                    GenomeScores.relevances
                )
                .join(Movies, MovieMetadata.movieId == Movies.movieId)
                .outerjoin(Ratings, MovieMetadata.movieId == Ratings.movieId)
                .join(GenomeScores, MovieMetadata.movieId == GenomeScores.movieId)
                .filter(MovieMetadata.movieId != movie_id)
                .group_by(
                    MovieMetadata.movieId,
                    MovieMetadata.title,
                    MovieMetadata.poster_path,
                    MovieMetadata.vote_average,
                    MovieMetadata.popularity,
                    Movies.genres,
                    GenomeScores.relevances
                )
                .order_by(MovieMetadata.popularity.desc())
            )
            high_score_movies_query_statement = str(high_score_movies_query.statement.compile(compile_kwargs={"literal_binds": True}))
            high_score_movies_results = high_score_movies_query.all()
            
            # Filter results in Python to find movies with high scores for the top tags
            filtered_results = []
            for movie in high_score_movies_results:
                if not movie.relevances:
                    continue
                    
                # Check if movie has high scores for any of the top tags
                for tag_id, base_relevance in top_tags:
                    if str(tag_id) in movie.relevances:
                        movie_relevance = float(movie.relevances[str(tag_id)])
                        if movie_relevance > base_relevance * 0.7:
                            filtered_results.append(movie)
                            break
            
            results.extend(filtered_results[:3*limit])
        
        # Similar Movies Approach 2: Same production company and genres
        if base_movie.production_companies:
            # Extract company IDs from base movie
            base_company_ids = {company['id'] for company in base_movie.production_companies}
            
            # Get movies from the same production companies
            movies_with_companies = (
                session.query(
                    MovieMetadata.movieId,
                    MovieMetadata.title,
                    MovieMetadata.poster_path,
                    MovieMetadata.vote_average,
                    MovieMetadata.popularity,
                    Movies.genres,
                    MovieMetadata.production_companies,
                    func.avg(Ratings.rating).label('user_rating')
                )
                .join(Movies, MovieMetadata.movieId == Movies.movieId)
                .outerjoin(Ratings, MovieMetadata.movieId == Ratings.movieId)
                .filter(MovieMetadata.movieId != movie_id)
                .filter(MovieMetadata.production_companies.isnot(None))
                .group_by(
                    MovieMetadata.movieId,
                    MovieMetadata.title,
                    MovieMetadata.poster_path,
                    MovieMetadata.vote_average,
                    MovieMetadata.popularity,
                    Movies.genres,
                    MovieMetadata.production_companies
                )
                .order_by(MovieMetadata.popularity.desc())
            )
            movies_with_companies_query_statement = str(movies_with_companies.statement.compile(compile_kwargs={"literal_binds": True}))
            movies_with_companies_results = movies_with_companies.all()
            
            # Filter movies that share at least one production company and genre
            filtered_results = []
            for movie in movies_with_companies_results:
                if not movie.production_companies:
                    continue
                    
                movie_company_ids = {company['id'] for company in movie.production_companies}
                if base_company_ids & movie_company_ids and any(genre in base_movie.genres for genre in movie.genres):
                    filtered_results.append(movie)
                    if len(filtered_results) >= limit:
                        break
            
            results.extend(filtered_results[:2*limit])
        
        # Similar Movies Approach 3: Similar genres only
        similar_genres_query = (
            session.query(
                MovieMetadata.movieId,
                MovieMetadata.title,
                MovieMetadata.poster_path,
                MovieMetadata.vote_average,
                MovieMetadata.popularity,
                Movies.genres,
                func.avg(Ratings.rating).label('user_rating')
            )
            .join(Movies, MovieMetadata.movieId == Movies.movieId)
            .outerjoin(Ratings, MovieMetadata.movieId == Ratings.movieId)
            .filter(MovieMetadata.movieId != movie_id)
            .group_by(
                MovieMetadata.movieId,
                MovieMetadata.title,
                MovieMetadata.poster_path,
                MovieMetadata.vote_average,
                MovieMetadata.popularity,
                Movies.genres
            )
            .order_by(MovieMetadata.popularity.desc())
            .limit(limit * 2)  # Get more results to filter
        )
        similar_genres_query_statement = str(similar_genres_query.statement.compile(compile_kwargs={"literal_binds": True}))
        similar_genres_results = similar_genres_query.all()

        # Filter by genre similarity and sort
        filtered_results = [r for r in similar_genres_results if any(genre in base_movie.genres for genre in r.genres)]
        results.extend(sorted(
            filtered_results,
            key=lambda x: x.popularity or 0,
            reverse=True
        )[:limit])

        # Remove duplicates by id
        unique_results = []
        for r in results:
            if r.movieId not in [ur.movieId for ur in unique_results]:
                unique_results.append(r)
        
        if len(unique_results) > limit:
            unique_results = random.sample(unique_results, limit)
        
        # Format results
        return {
            'movies': [
                {
                    'movieId': r.movieId,
                    'title': r.title,
                    'poster_path': r.poster_path,
                    'vote_average': r.vote_average,
                    'genres': r.genres,
                'user_rating': float(r.user_rating) if r.user_rating else None,
                }
                for r in unique_results
            ],
            'high_score_movies_query_statement': high_score_movies_query_statement,
            'similar_genres_query_statement': similar_genres_query_statement,
            'movies_with_companies_query_statement': movies_with_companies_query_statement
        }
    except Exception as e:
        logger.error(f"Error in get_similar_movies: {str(e)}", exc_info=True)
        raise

def get_actor_info(session, actor_id):
    """Get actor information and their movie appearances."""
    try:
        # Detect database dialect
        dialect_name = session.bind.dialect.name
        
        # First get all movies where this actor appears in the cast
        movies_query = (
            session.query(
                Credits.cast_,
                MovieMetadata.movieId,
                MovieMetadata.title,
                MovieMetadata.poster_path,
                MovieMetadata.release_date,
                MovieMetadata.vote_average,
                Movies.genres
            )
            .join(MovieMetadata, Credits.movieId == MovieMetadata.movieId)
            .join(Movies, MovieMetadata.movieId == Movies.movieId)
        )
        
        # Apply dialect-specific JSON filtering
        if dialect_name == 'cockroachdb':
            movies_query = movies_query.filter(
                Credits.cast_.op('@>')(cast([{"id": int(actor_id)}], JSONB))
            )
        elif dialect_name == 'mariadb' or dialect_name == 'mysql':
            # For MariaDB/MySQL, use JSON_SEARCH to find the actor ID in the cast array
            movies_query = movies_query.filter(
                func.json_search(
                    Credits.cast_,
                    'one',
                    str(actor_id),
                    None,
                    '$[*].id'
                ).isnot(None)
            )
        else:
            # For PostgreSQL and others that support jsonb_path_exists
            movies_query = movies_query.filter(
                func.jsonb_path_exists(
                    Credits.cast_,
                    f'$[*] ? (@.id == {actor_id})'
                )
            )
        
        movies = []
        actor_details = None

        # Just use str() on the statement without literal_binds
        movies_query_statement = str(movies_query.statement)
        logger.info(f"Actor movies query: {movies_query_statement}")
        
        for movie in movies_query.all():
            # Extract actor details from cast if not already found
            if not actor_details:
                cast_list = movie.cast_ if isinstance(movie.cast_, list) else []
                for cast_member in cast_list:
                    if str(cast_member.get('id')) == str(actor_id):
                        actor_details = {
                            'id': cast_member.get('id'),
                            'name': cast_member.get('name'),
                            'profile_path': cast_member.get('profile_path'),
                            'character': cast_member.get('character'),
                            'order': cast_member.get('order'),
                            'gender': cast_member.get('gender')
                        }
                        break
            
            # Add movie to the list
            movies.append({
                'movieId': movie.movieId,
                'title': movie.title,
                'poster_path': movie.poster_path,
                'release_date': movie.release_date.isoformat() if movie.release_date else None,
                'vote_average': movie.vote_average,
                'genres': movie.genres
            })
        
        if not actor_details:
            return None
            
        # Sort movies by release date
        movies.sort(key=lambda x: x.get('release_date', ''), reverse=True)
        
        return {
            'actor': actor_details,
            'movies': movies,
            'total_movies': len(movies),
            'movies_query_statement': movies_query_statement
        }
        
    except Exception as e:
        logger.error(f"Error in get_actor_info: {str(e)}", exc_info=True)
        raise
