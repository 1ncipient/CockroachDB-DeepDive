#!/usr/bin/env python3
import os
import pandas as pd
import argparse
import dotenv

from sqlalchemy import create_engine, inspect, text, MetaData, event
from psycopg2.errors import SerializationFailure
from sqlalchemy.exc import OperationalError, SQLAlchemyError, InternalError
from movieRatingSystem.models.movie_models import *
from movieRatingSystem.logging_config import get_logger
from movieRatingSystem.config.database import DatabaseConfig
from sqlalchemy.ext.automap import automap_base

logger = get_logger()

MAX_RETRIES = 10

def createTables(engine, drop=False):
    if drop:
        logger.info("Dropping all Tables!")
        Base.metadata.drop_all(engine)

    try:
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully!")
    except Exception as e: 
        logger.error(f"An error occurred: {e}")

def showTables(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in the database: {tables}")
    
    for table_name in tables:
        table = Base.metadata.tables.get(table_name)
        if table is not None:
            table.metadata.reflect(bind=engine)

def uploadTablesData(db_type, file_path, table_name, engine, chunk_size):
    logger.info(f"Inserting [{file_path}] into table [{table_name}] for {db_type} database")

    # Safe truncation with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            connection = engine.connect()
            transaction = connection.begin()
            with open(file_path, 'r', newline=None) as file:
                df = pd.read_csv(file)
                if db_type == 'mariadb' and table_name == 'movies':
                    # MariaDB does not support ARRAY type, so we need to convert the genres column to a JSON string
                    df['genres'] = df['genres'].apply(lambda x: json.dumps([x.strip() for x in x[1:-1].split(',') if x.strip()]))
                    df.to_sql(table_name, con=connection, index=False, if_exists='append', chunksize=chunk_size, method='multi')
                else:
                    df.to_sql(table_name, con=connection, index=False, if_exists='append', chunksize=chunk_size, method='multi')
                transaction.commit()
                logger.info(f"Data inserted into [{table_name}] successfully.")
            break
        except (SerializationFailure, OperationalError, InternalError) as e:
            logger.error(f"Failed to upload data to table [{table_name}]: {e}")
            if attempt < MAX_RETRIES - 1:
                transaction.rollback()
                chunk_size = chunk_size // 3
                logger.info(f"Retrying transaction for table [{table_name}] (attempt {attempt + 1}, chunk size: {chunk_size})...")
            else:   
                raise SQLAlchemyError("Transaction maximum retry reached!\n")
        except SQLAlchemyError as e:
            logger.error(f"Failed to upload data to table [{table_name}]: {e}")
            raise e

def main():
    parser = argparse.ArgumentParser(description="Set up database for MovieLens.")
    parser.add_argument("--db_type", help="The type of database to use")
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="If set, clean the database before setup."
    )
    parser.add_argument("path", help="The path to process")
    args = parser.parse_args()

    logger.info(f"Running with database type: {args.db_type} and clean flag: {args.clean}")

    data_path = args.path
    
    try:
        match args.db_type:
            case 'cockroach':
                engine = DatabaseConfig().get_engine(args.db_type)
                createTables(engine, args.clean)
                showTables(engine)
                
                # Uploading dataset tables
                uploadTablesData(args.db_type, data_path + MovieMetadata.filename, MovieMetadata.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + Credits.filename, Credits.__tablename__, engine, 2000)
                uploadTablesData(args.db_type, data_path + Links.filename, Links.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + Movies.filename, Movies.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + Ratings.filename, Ratings.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + GenomeTags.filename, GenomeTags.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + GenomeScores.filename, GenomeScores.__tablename__, engine, 2000)

                engine.dispose()
            case 'postgres':
                engine = DatabaseConfig().get_engine(args.db_type)
                createTables(engine, args.clean)
                showTables(engine)
                
                # Uploading dataset tables
                uploadTablesData(args.db_type, data_path + MovieMetadata.filename, MovieMetadata.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + Credits.filename, Credits.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + Links.filename, Links.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + Movies.filename, Movies.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + Ratings.filename, Ratings.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + GenomeTags.filename, GenomeTags.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + GenomeScores.filename, GenomeScores.__tablename__, engine, 100000)

                engine.dispose()
            case 'mariadb':
                engine = DatabaseConfig().get_engine(args.db_type)
                createTables(engine, args.clean)
                showTables(engine)
                
                # Uploading dataset tables
                uploadTablesData(args.db_type, data_path + MovieMetadata.filename, MovieMetadata.__tablename__, engine, 100000)    
                uploadTablesData(args.db_type, data_path + Credits.filename, Credits.__tablename__, engine, 50000)
                uploadTablesData(args.db_type, data_path + Links.filename, Links.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + Movies.filename, Movies.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + Ratings.filename, Ratings.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + GenomeTags.filename, GenomeTags.__tablename__, engine, 100000)
                uploadTablesData(args.db_type, data_path + GenomeScores.filename, GenomeScores.__tablename__, engine, 100000)

                engine.dispose()
            case _:
                raise ValueError(f"Unsupported database type: {args.db_type}")
    except Exception as e:
        logger.error(f"Failed to connect to database.")
        logger.error(f"{e}")
        return

if __name__ == '__main__':
    main()
    