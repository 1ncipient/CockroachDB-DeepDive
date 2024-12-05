from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, ForeignKey, create_engine
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()

class MovieMetadata(Base):
    filename = 'movies_metadata.csv'
    __tablename__ = 'movie_metadata'
    
    movieId = Column(Integer, primary_key=True, nullable=False)
    adult = Column(Boolean, nullable=True)
    backdrop_path = Column(String, nullable=True)
    budget = Column(Integer, nullable=True)
    original_language = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    popularity = Column(Float, nullable=True)
    poster_path = Column(String, nullable=True)
    production_companies = Column(JSONB, nullable=True)
    production_countries = Column(JSONB, nullable=True)
    release_date = Column(Date, nullable=True)
    revenue = Column(Integer, nullable=True)
    runtime = Column(Integer, nullable=True)
    spoken_languages = Column(JSONB, nullable=True)
    tagline = Column(Text, nullable=True)
    title = Column(String, nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)

class Credits(Base):
    filename = 'credits.csv'
    __tablename__ = 'credits'
    
    movieId = Column(Integer, primary_key=True, nullable=False)
    cast = Column(JSONB, nullable=True)
    crew = Column(JSONB, nullable=True)

class Links(Base):
    filename = 'links.csv'
    __tablename__ = 'links'
    
    movieId = Column(Integer, primary_key=True, nullable=False)
    imdbId = Column(Integer, nullable=True)
    tmdbId = Column(Integer, nullable=True)

class Movies(Base):
    filename = 'movies.csv'
    __tablename__ = 'movies'
    
    movieId = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=True)
    genres = Column(ARRAY(String), nullable=True)

    genome_scores = relationship('GenomeScores', back_populates='movie')

class Ratings(Base):
    filename = 'ratings.csv'
    __tablename__ = 'ratings'
    
    movieId = Column(Integer, primary_key=True, nullable=False)
    rating = Column(Float, nullable=True)
class GenomeTags(Base):
    filename = 'genome-tags.csv'
    __tablename__ = 'genome_tags'
    
    tagId = Column(Integer, primary_key=True, nullable=False)
    tag = Column(String, nullable=True)

class GenomeScores(Base):
    filename = 'genome-scores.csv'
    __tablename__ = 'genome_scores'
    
    movieId = Column(Integer, ForeignKey('movies.movieId'), primary_key=True, nullable=False)
    relevances = Column(JSONB, nullable=True)
    
    movie = relationship('Movies', back_populates='genome_scores')


engine = create_engine('cockroachdb://victor:sgOo4WtHFSbGxZxhyMw6jg@movie-rating-system-3020.jxf.cockroachlabs.cloud:26257/moviedb?sslmode=verify-full')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)