#!/usr/bin/env python3

import os
import pandas as pd
import argparse

from sqlalchemy import create_engine, inspect, text
from model.movie_models import *

MAX_RETRIES = 5

def createTables(engine, drop=False):
    if drop:
        print("Dropping all Table!\n")
        Base.metadata.drop_all(engine)

    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully!\n")
    except Exception as e: 
        print(f"An error occurred: {e}\n")

def showTables(engine):
    # Get the inspector for the engine
    inspector = inspect(engine)

    # List all tables in the database
    tables = inspector.get_table_names()
    print("Tables in the database:", tables, '\n')

    return tables

def uploadTablesData(file_path, table_name, engine, chunk_size):
    print(f"Inserting [{file_path}] into table [{table_name}]\n")

    with engine.connect() as con:
        # Safe truncation with retry logic
        for attempt in range(MAX_RETRIES):
            try:

                # Upload data to the table
                df = pd.read_csv(open(file_path,'r', newline=None))
                df.to_sql(table_name, con=engine, index=False, if_exists='append', chunksize=chunk_size, method='multi')
                print(f"Data inserted into [{table_name}] successfully.\n")
                break
            except Exception as e:
                if ("TransactionAbortedError" in str(e) or "TransactionRetryError" in str(e)) and attempt < MAX_RETRIES - 1:
                    print(f"Retrying transaction for table [{table_name}] (attempt {attempt + 1})...")
                    continue
                else:
                    print(f"Failed to upload data to table [{table_name}]: {e}\n")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Set up CockroachDB for MovieLens.")
    parser.add_argument("path", help="The path to process")
    parser.add_argument(
        "-clean", 
        action="store_true", 
        help="If set, clean the database before setup."
    )
    args = parser.parse_args()

    # Get the path from the arguments
    data_path = args.path

    # Validate DATABASE_URL
    if "DATABASE_URL" not in os.environ:
        print("Error: DATABASE_URL environment variable is not set.\n")
        return

    try:
        engine = create_engine(os.environ["DATABASE_URL"], connect_args={"application_name": "movieDB", "options": "--retry_write=true"})
        print("Database connection successful.\n")
    except Exception as e:
        print("Failed to connect to database.\n")
        print(f"{e}")

    createTables(engine, args.clean)
    showTables(engine)
    
    # Uploading dataset tables to CockroachDB Cloud.
    uploadTablesData(data_path + MovieMetadata.filename, MovieMetadata.__tablename__, engine, 50000)
    uploadTablesData(data_path + Credits.filename, Credits.__tablename__, engine, 2000)
    uploadTablesData(data_path + Links.filename, Links.__tablename__, engine, 50000)
    uploadTablesData(data_path + Movies.filename, Movies.__tablename__, engine, 50000)
    uploadTablesData(data_path + Ratings.filename, Ratings.__tablename__, engine, 50000)
    uploadTablesData(data_path + GenomeTags.filename, GenomeTags.__tablename__, engine, 50000)
    uploadTablesData(data_path + GenomeScores.filename, GenomeScores.__tablename__, engine, 2000)

    engine.dispose()
    

if __name__ == '__main__':
    main()
    