#!/usr/bin/env python3

import json
import ast
import argparse
import pandas as pd

def unify_movieId(movies_metadata, credits, links, genome_scores, movies, ratings):
    # Drop all duplicate and null values
    movies_metadata.drop_duplicates(subset='id', keep='first', inplace=True)
    movies_metadata.drop_duplicates(subset='imdb_id', keep='first', inplace=True)
    credits.drop_duplicates(subset='id', keep='first', inplace=True)
    links.drop_duplicates(subset='tmdbId', keep='first', inplace=True)
    movies_metadata['imdbId'] = movies_metadata['imdb_id'].str.lstrip('tt').astype('float')

    # Unify movie id across tables
    tmdb_to_movieId_map = dict(zip(links['tmdbId'], links['movieId']))
    movies_metadata['movieId'] = movies_metadata['id'].map(tmdb_to_movieId_map)
    credits['movieId'] = credits['id'].map(tmdb_to_movieId_map)

    # intersect movie id across tables to keep the common movies
    valid_movieIds = set(links['movieId'].dropna()) & \
                    set(credits['movieId'].dropna()) & \
                    set(movies_metadata['movieId'].dropna())
    
    links = links[links['movieId'].isin(valid_movieIds)]
    credits = credits[credits['movieId'].isin(valid_movieIds)]
    movies_metadata = movies_metadata[movies_metadata['movieId'].isin(valid_movieIds)]
    genome_scores = genome_scores[genome_scores['movieId'].isin(valid_movieIds)]
    movies = movies[movies['movieId'].isin(valid_movieIds)]
    ratings = ratings[ratings['movieId'].isin(valid_movieIds)]

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a path argument.")
    parser.add_argument("path", help="The path to process")
    args = parser.parse_args()
    
    # Get the path from the arguments
    data_path = args.path

    movies_metadata = pd.read_csv(open(data_path + 'movies_metadata.csv','r', newline=None))
    credits = pd.read_csv(open(data_path + 'credits.csv','r', newline=None))
    links = pd.read_csv(open(data_path + 'links.csv','r', newline=None))
    genome_scores = pd.read_csv(open(data_path + 'genome-scores.csv','r', newline=None))
    movies = pd.read_csv(open(data_path + 'movies.csv','r', newline=None))
    ratings = pd.read_csv(open(data_path + 'ratings.csv','r', newline=None))

    unify_movieId(movies_metadata, credits, links, genome_scores, movies, ratings)

    # Remove unnecessary columns in movie metadata
    movies_metadata.drop(columns=['belongs_to_collection', 'genres', 'homepage', 'status', 'original_title', 'video', 'imdb_id', 'id', 'imdbId'], inplace=True, errors='ignore')

    # Format the json data
    movies_metadata['production_companies'] = movies_metadata['production_companies'].apply(ast.literal_eval).apply(lambda x: json.dumps(x))
    movies_metadata['production_countries'] = movies_metadata['production_countries'].apply(ast.literal_eval).apply(lambda x: json.dumps(x))
    movies_metadata['spoken_languages'] = movies_metadata['spoken_languages'].apply(ast.literal_eval).apply(lambda x: json.dumps(x))

    # Format the json data
    credits['cast'] = credits['cast'].apply(ast.literal_eval).apply(lambda x: json.dumps(x))
    credits['crew'] = credits['crew'].apply(ast.literal_eval).apply(lambda x: json.dumps(x))

    credits.drop(columns='id', inplace=True, errors='ignore')

    movies['genres'] = movies['genres'].fillna('').str.replace('|', ',', regex=False).apply(lambda x: f'{{{x}}}' if x else '{}')

    genome_scores = genome_scores.groupby("movieId").apply(lambda x: json.dumps(dict(zip(x["tagId"], x["relevance"])))).reset_index(name="relevances")

    ratings.drop(columns=['userId', 'timestamp'], inplace=True, errors='ignore')
    ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
    ratings = ratings.sort_values(by='movieId')

    movies_metadata.to_csv(data_path + 'movies_metadata.csv', index=False)
    credits.to_csv(data_path + 'credits.csv', index=False)
    links.to_csv(data_path + 'links.csv', index=False)
    movies.to_csv(data_path + 'movies.csv', index=False)
    ratings.to_csv(data_path + 'ratings.csv', index=False)
    genome_scores.to_csv(data_path + 'genome-scores.csv', index=False)

    
if __name__ == '__main__':
    main()
