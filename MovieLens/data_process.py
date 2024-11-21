#!/usr/bin/env python3

import argparse
import pandas as pd

def unify_movieId(data_path):
    movies_metadata = pd.read_csv(data_path + 'movies_metadata.csv')
    credits = pd.read_csv(data_path + 'credits.csv')
    links = pd.read_csv(data_path + 'links.csv')

    # movies_metadata.columns = [x.replace("\r", "") for x in movies_metadata.columns.to_list()]

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

    movies = pd.read_csv(data_path + 'movies.csv')
    ratings = pd.read_csv(data_path + 'ratings.csv')
    tags = pd.read_csv(data_path + 'tags.csv')

    movies['genres'] = movies['genres'].fillna('').str.replace('|', ',', regex=False).apply(lambda x: f'{{{x}}}' if x else '{}')

    tags.drop(columns=['userId', 'timestamp'], inplace=True, errors='ignore')
    tags['tag'] = tags['tag'].fillna('').astype(str)
    tags = tags.groupby('movieId')['tag'].apply(lambda tags: '{' + ','.join(sorted(set(tag.replace(',', '\\,') for tag in tags if tag.strip()))) + '}').reset_index().sort_values(by='movieId')
    tags.rename(columns={'tag': 'tags'}, inplace=True)

    ratings.drop(columns=['userId', 'timestamp'], inplace=True, errors='ignore')
    ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
    ratings = ratings.sort_values(by='movieId')

    movies = movies[movies['movieId'].isin(valid_movieIds)]
    ratings = ratings[ratings['movieId'].isin(valid_movieIds)]
    tags = tags[tags['movieId'].isin(valid_movieIds)]

    movies_metadata.to_csv(data_path + 'movies_metadata.csv', index=False)
    credits.to_csv(data_path + 'credits.csv', index=False)
    links.to_csv(data_path + 'links.csv', index=False)
    movies.to_csv(data_path + 'movies.csv', index=False)
    ratings.to_csv(data_path + 'ratings.csv', index=False)
    tags.to_csv(data_path + 'tags.csv', index=False)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a path argument.")
    parser.add_argument("path", help="The path to process")
    args = parser.parse_args()

    # Get the path from the arguments
    data_path = args.path

    unify_movieId(data_path)

    movies_metadata = pd.read_csv(data_path + 'movies_metadata.csv', lineterminator='\n')
    credits = pd.read_csv(data_path + 'credits.csv', lineterminator='\n')
    
    # Remove unnecessary columns in movie metadata
    movies_metadata.drop(columns=['belongs_to_collection', 'genres', 'homepage', 'status', 'original_title', 'video', 'imdb_id', 'id', 'imdbId'], inplace=True, errors='ignore')

    # Format the json data
    movies_metadata['production_companies'] = movies_metadata['production_companies'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    movies_metadata['production_countries'] = movies_metadata['production_countries'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    movies_metadata['spoken_languages'] = movies_metadata['spoken_languages'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')

    movies_metadata.drop(columns='id', inplace=True, errors='ignore')

    # Format the json data
    credits['cast'] = credits['cast'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    credits['crew'] = credits['crew'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')

    movies_metadata.to_csv(data_path + 'movies_metadata.csv', index=False)
    credits.to_csv(data_path + 'credits.csv', index=False)

    
if __name__ == '__main__':
    main()
