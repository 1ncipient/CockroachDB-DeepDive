from sqlalchemy import func, and_, or_, Integer, Float, select, text, desc, asc
from sqlalchemy.orm import Session
from movieRatingSystem.models.movie_models import MovieMetadata, Movies, Ratings, Credits, Links, GenomeScores, GenomeTags
from typing import Optional, List, Dict, Any
from datetime import date
import logging
import shutil
from sqlalchemy.dialects import postgresql
from sqlalchemy import String

logger = logging.getLogger(__name__)

class MovieQueryBuilder:
    def __init__(self, session: Session):
        self.session = session
        self.query = None
        self.conditions = []

    def base_query(self):
        """Initialize the base query with all necessary columns."""
        self.query = (
            select(
                MovieMetadata.movieId,
                MovieMetadata.title,
                MovieMetadata.adult,
                MovieMetadata.release_date,
                MovieMetadata.original_language,
                MovieMetadata.runtime,
                MovieMetadata.vote_average,
                MovieMetadata.vote_count,
                MovieMetadata.popularity,
                MovieMetadata.poster_path,
                MovieMetadata.overview,
                MovieMetadata.tagline,
                Movies.genres,
                func.avg(Ratings.rating).label('user_rating')
            )
            .join(Movies, MovieMetadata.movieId == Movies.movieId)
            .outerjoin(Ratings, MovieMetadata.movieId == Ratings.movieId)
            .group_by(
                MovieMetadata.movieId,
                Movies.genres
            )
        )
        return self

    def filter_by_movie_id(self, movie_id: int):
        """Add movie ID filter."""
        if movie_id:
            self.conditions.append(MovieMetadata.movieId == movie_id)
        return self

    def filter_by_title(self, title: Optional[str]):
        """Add title filter."""
        if title:
            self.conditions.append(MovieMetadata.title.ilike(f'%{title}%'))
        return self

    def filter_by_genres(self, genres: Optional[List[str]]):
        """Add genres filter."""
        if genres:
            genre_conditions = [Movies.genres.contains([genre]) for genre in genres]
            self.conditions.append(or_(*genre_conditions))
        return self

    def filter_by_languages(self, languages: Optional[List[str]]):
        """Add languages filter."""
        if languages:
            self.conditions.append(MovieMetadata.original_language.in_(languages))
        return self

    def filter_by_years(self, years: Optional[tuple]):
        """Add year range filter."""
        if years and len(years) == 2:
            start_year, end_year = years
            self.conditions.append(
                func.extract('year', MovieMetadata.release_date).between(
                    int(start_year), int(end_year)
                )
            )
            logger.info(f"Added year filter: {start_year} to {end_year}")
        return self

    def filter_by_rating_range(self, min_rating: float, max_rating: float):
        """Add rating range filter."""
        self.conditions.append(MovieMetadata.vote_average.between(min_rating, max_rating))
        return self

    def filter_by_runtime_range(self, min_runtime: int, max_runtime: int):
        """Add runtime range filter."""
        self.conditions.append(MovieMetadata.runtime.between(min_runtime, max_runtime))
        return self

    def filter_by_adult_content(self, include_adult: bool = False):
        """Add adult content filter."""
        if not include_adult:
            self.conditions.append(MovieMetadata.adult.is_(False))
        return self

    def filter_by_keywords(self, keywords: Optional[List[str]]):
        """Add keyword filter using genome scores."""
        if keywords:
            # Create a subquery to find movies with matching tags and high relevance
            relevant_movies = (
                select(GenomeScores.movieId)
                .select_from(GenomeScores)
                .join(
                    GenomeTags,
                    and_(
                        GenomeTags.tag.in_(keywords),
                        func.jsonb_extract_path_text(
                            GenomeScores.relevances,
                            func.cast(GenomeTags.tagId, String)
                        ).cast(Float) > 0.7
                    )
                )
                .group_by(GenomeScores.movieId)
            ).scalar_subquery()

            # Add the condition to the main query
            self.conditions.append(
                MovieMetadata.movieId.in_(relevant_movies)
            )

        return self

    def apply_sorting(self, sort_by: Optional[str]):
        """Apply sorting at the database level based on the specified field."""
        if not sort_by:
            # Default sort by popularity descending
            self.query = self.query.order_by(desc(MovieMetadata.popularity))
            return self

        sort_config = {
            'rating': MovieMetadata.vote_average,
            'popularity': MovieMetadata.popularity,
            'release_date': MovieMetadata.release_date,
            'title': MovieMetadata.title
        }

        if sort_by in sort_config:
            column = sort_config[sort_by]
            # Sort in descending order for all except title
            if sort_by == 'title':
                self.query = self.query.order_by(asc(column))
            else:
                self.query = self.query.order_by(desc(column))

        return self

    def paginate(self, page: int = 1, items_per_page: int = 20) -> Dict[str, Any]:
        """Execute the query with pagination and return results."""
        from sqlalchemy.dialects import postgresql

        # Apply all conditions
        if self.conditions:
            self.query = self.query.where(and_(*self.conditions))

        # Get total count using a separate count query
        count_stmt = (
            select(func.count(func.distinct(MovieMetadata.movieId)))
            .select_from(MovieMetadata)
            .join(Movies, MovieMetadata.movieId == Movies.movieId)
        )
        
        # Apply the same conditions to the count query
        if self.conditions:
            count_stmt = count_stmt.where(and_(*self.conditions))
        
        # Log the count query
        count_sql = str(count_stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
        logger.info("Count SQL Query:" + '\n' + count_sql)
        
        total_count = self.session.execute(count_stmt).scalar()

        # Get paginated results
        offset = (page - 1) * items_per_page
        stmt = (
            self.query
            .limit(items_per_page)
            .offset(offset)
        )
        
        # Log the final SQL query
        sql_query = str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
        logger.info("Main SQL Query:" + '\n' + sql_query)
        
        results = self.session.execute(stmt).all()

        return {
            'total_count': total_count,
            'results': [dict(row._mapping) for row in results],
            'query_statement': sql_query
        }