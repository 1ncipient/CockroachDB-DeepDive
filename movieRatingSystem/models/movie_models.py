from sqlalchemy import Column, BigInteger, String, Float, Boolean, Text, Date, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import event, text
from sqlalchemy.types import TypeDecorator, UserDefinedType
from movieRatingSystem.logging_config import get_logger
import json
import re

logger = get_logger()

Base = declarative_base()

class MariaDBJSON(UserDefinedType):
    def get_col_spec(self, **kw):
        return "JSON"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return json.dumps(value)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            data = json.loads(value)
            return data
        return process

# MariaDB does not support JSONB or ARRAY types, so we need to convert them to JSON
def get_column_type(dialect_name, original_type):
    """Helper function to determine the appropriate column type based on dialect."""
    if isinstance(original_type, JSONB):
        if dialect_name in ("mysql", "mariadb"):
            return MariaDBJSON()
        return original_type
    elif isinstance(original_type, ARRAY):
        if dialect_name in ("mysql", "mariadb"):
            return MariaDBJSON()
        return original_type
    return original_type

@event.listens_for(Base.metadata, 'before_create')
def adapt_column_type(target, connection, **kw):
    dialect_name = connection.dialect.name
    for table in target.tables.values():
        for column in table.columns:
            new_type = get_column_type(dialect_name, column.type)
            if new_type != column.type:
                column.type = new_type

class MovieMetadata(Base):
    filename = 'movies_metadata.csv'
    __tablename__ = 'movie_metadata'
    
    movieId = Column(BigInteger , primary_key=True, nullable=False)
    adult = Column(Boolean, nullable=True)
    backdrop_path = Column(String(255), nullable=True)
    budget = Column(BigInteger , nullable=True)
    original_language = Column(String(255), nullable=True)
    overview = Column(Text, nullable=True)
    popularity = Column(Float, nullable=True)
    poster_path = Column(String(255), nullable=True)
    production_companies = Column(JSONB, nullable=True)
    production_countries = Column(JSONB, nullable=True)
    release_date = Column(Date, nullable=True)
    revenue = Column(BigInteger , nullable=True)
    runtime = Column(BigInteger , nullable=True)
    spoken_languages = Column(JSONB, nullable=True)
    tagline = Column(Text, nullable=True)
    title = Column(String(255), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(BigInteger , nullable=True)

    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_movie_popularity', 'popularity'),
        Index('idx_movie_vote_average', 'vote_average'),
        Index('idx_movie_runtime', 'runtime'),
        Index('idx_movie_original_language', 'original_language'),
        Index('idx_movie_release_date', 'release_date'),
        # Add full-text search indexes for MariaDB
        Index('idx_movie_title_fulltext', 'title', mysql_prefix='FULLTEXT'),
        Index('idx_movie_overview_fulltext', 'overview', mysql_prefix='FULLTEXT'),
        Index('idx_movie_tagline_fulltext', 'tagline', mysql_prefix='FULLTEXT'),
    )

    def __repr__(self):
        return f"<MovieMetadata(movieId={self.movieId}, title='{self.title}')>"

class Movies(Base):
    filename = 'movies.csv'
    __tablename__ = 'movies'
    
    movieId = Column(BigInteger , primary_key=True, nullable=False)
    title = Column(String(255), nullable=True)
    genres = Column(ARRAY(String(255)), nullable=True)

    __table_args__ = (
        # Add full-text search index for title
        Index('idx_movies_title_fulltext', 'title', mysql_prefix='FULLTEXT'),
    )

    def __repr__(self):
        return f"<Movies(movieId={self.movieId}, title='{self.title}')>"

class Ratings(Base):
    filename = 'ratings.csv'
    __tablename__ = 'ratings'

    movieId = Column(BigInteger , primary_key=True, nullable=False)
    rating = Column(Float, nullable=True)

    __table_args__ = (
        Index('idx_ratings_movieid', 'movieId'),
        Index('idx_ratings', 'rating'),
    )

    def __repr__(self):
        return f"<Ratings(userId={self.userId}, movieId={self.movieId}, rating={self.rating})>"

class Credits(Base):
    filename = 'credits.csv'
    __tablename__ = 'credits'

    movieId = Column('movieId', BigInteger, primary_key=True)
    # avoid using cast as it is a reserved word in SQL
    cast_ = Column('cast', JSONB, nullable=True)
    crew = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<Credits(movieId={self.movieId})>"

class Links(Base):
    filename = 'links.csv'
    __tablename__ = 'links'

    movieId = Column(BigInteger, primary_key=True, nullable=False)
    imdbId = Column(BigInteger, nullable=True)
    tmdbId = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<Links(movieId={self.movieId})>"

class GenomeTags(Base):
    filename = 'genome-tags.csv'
    __tablename__ = 'genome_tags'

    tagId = Column(BigInteger , primary_key=True, nullable=False)
    tag = Column(String(255), nullable=False)

    __table_args__ = (
        Index('idx_genome_tags_tagid', 'tagId'),
        Index('idx_genome_tags_tag', 'tag'),
    )

    def __repr__(self):
        return f"<GenomeTags(tagId={self.tagId}, tag='{self.tag}')>"

class GenomeScores(Base):
    filename = 'genome-scores.csv'
    __tablename__ = 'genome_scores'
    
    movieId = Column(BigInteger, primary_key=True, nullable=False)
    relevances = Column(JSONB, nullable=True)

    __table_args__ = (
        Index('idx_genome_scores_movieid', 'movieId'),
    )

    def __repr__(self):
        return f"<GenomeScores(movieId={self.movieId}, tagId={self.tagId})>"
