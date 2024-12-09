#!/bin/bash

SCRIPT_PATH=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT_PATH")

MOVIE_RATING_SYSTEM_PATH="$DIR/../movieRatingSystem"
MOVIE_LENS_PATH="$DIR/../MovieLens"

# Check if the path is already in PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$MOVIE_RATING_SYSTEM_PATH:"* ]]; then
    # Add the path to PYTHONPATH
    export PYTHONPATH="$PYTHONPATH:$MOVIE_RATING_SYSTEM_PATH"
fi

GREEN_COLOR='\033[1;32m'
RED_COLOR='\033[0;31m'
NO_COLOR='\033[0m'

# Function to setup a specific database
setup_database() {
    local db_type=$1
    local clean_flag=$2
    
    case $db_type in
        "cockroach")
            if [ "$clean_flag" = true ]; then
                echo -e "\n${GREEN_COLOR}Setting up CockroachDB for MovieLens${NO_COLOR}. Will delete existing data.\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" --db_type cockroach --clean "$MOVIE_LENS_PATH/"
            else
                echo -e "\n${GREEN_COLOR}Setting up CockroachDB for MovieLens${NO_COLOR}\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" "$MOVIE_LENS_PATH/"
            fi
            ;;
        "postgres")
            if [ "$clean_flag" = true ]; then
                echo -e "\n${GREEN_COLOR}Setting up PostgreSQL for MovieLens${NO_COLOR}. Will delete existing data.\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" --db_type postgres --clean "$MOVIE_LENS_PATH/"
            else
                echo -e "\n${GREEN_COLOR}Setting up PostgreSQL for MovieLens${NO_COLOR}\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" "$MOVIE_LENS_PATH/"
            fi
            ;;
        "mariadb")
            if [ "$clean_flag" = true ]; then
                echo -e "\n${GREEN_COLOR}Setting up MariaDB for MovieLens${NO_COLOR}. Will delete existing data.\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" --db_type mariadb --clean "$MOVIE_LENS_PATH/"    
            else
                echo -e "\n${GREEN_COLOR}Setting up MariaDB for MovieLens${NO_COLOR}\n"
                "$MOVIE_RATING_SYSTEM_PATH/utils/import_db.py" "$MOVIE_LENS_PATH/"
            fi
            ;;
        *)
            echo -e "\n${RED_COLOR}Invalid database type: $db_type${NO_COLOR}\n"
            return 1
            ;;
    esac
}

# Parse command line arguments
CLEAN_FLAG=false
DB_TYPES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--reset)
            CLEAN_FLAG=true
            shift
            ;;
        -d|--database)
            if [ -z "$2" ]; then
                echo -e "${RED_COLOR}Error: Database type required${NO_COLOR}"
                exit 1
            fi
            DB_TYPES+=("$2")
            shift 2
            ;;
        *)
            echo -e "${RED_COLOR}Unknown option: $1${NO_COLOR}"
            exit 1
            ;;
    esac
done

# If no database specified, use all
if [ ${#DB_TYPES[@]} -eq 0 ]; then
    DB_TYPES=("cockroach" "postgres" "mariadb")
fi

# Setup each specified database
for db_type in "${DB_TYPES[@]}"; do
    setup_database "$db_type" "$CLEAN_FLAG"
done

exit 0