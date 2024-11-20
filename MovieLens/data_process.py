#!/usr/bin/env python3

import argparse
import pandas as pd

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a path argument.")
    parser.add_argument("path", help="The path to process")
    args = parser.parse_args()

    # Get the path from the arguments
    data_path = args.path

    movies_metadata = pd.read_csv(data_path + 'movies_metadata.csv', lineterminator='\n')
    credits = pd.read_csv(data_path + 'credits.csv', lineterminator='\n')

    credits.columns = [x.replace("\r", "") for x in credits.columns.to_list()]
    movies_metadata.columns = [x.replace("\r", "") for x in movies_metadata.columns.to_list()]

    movies_metadata.drop(columns=['belongs_to_collection', 'genres', 'homepage', 'status', 'original_title', 'video'], inplace=True, errors='ignore')
    movies_metadata.rename(columns={'id' : 'tmdb_id'}, inplace=True)

    movies_metadata['production_companies'] = movies_metadata['production_companies'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    movies_metadata['production_countries'] = movies_metadata['production_countries'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    movies_metadata['spoken_languages'] = movies_metadata['spoken_languages'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')

    credits.rename(columns={'id' : 'tmdb_id'}, inplace=True)

    credits['cast'] = credits['cast'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')
    credits['crew'] = credits['crew'].str.replace("'", '"').str.replace("None", 'null').str.replace("True", 'true').str.replace("False", 'false')

    movies_metadata.to_csv(data_path + 'movies_metadata.csv', index=False)
    credits.to_csv(data_path + 'credits.csv', index=False)

    
if __name__ == '__main__':
    main()
