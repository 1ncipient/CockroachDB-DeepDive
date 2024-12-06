#!/bin/bash

SCRIPT_PATH=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT_PATH")

MOVIE_RATING_SYSTEM_PATH="$DIR/movie-rating-system"

# Check if the path is already in PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$MOVIE_RATING_SYSTEM_PATH:"* ]]; then
    # Add the path to PYTHONPATH
    export PYTHONPATH="$PYTHONPATH:$MOVIE_RATING_SYSTEM_PATH"
fi

GREEN_COLOR='\033[1;32m'
RED_COLOR='\033[0;31m'
NO_COLOR='\033[0m'

if  [[ $1 = "-r" ]]; then
    echo -e "\n${GREEN_COLOR}Setting up CockroachDB for MovieLens${NO_COLOR}\n"
    "$DIR/movie-rating-system/util/import_db.py" "$DIR/MovieLens/" "-clean"
else
    echo -e "\n${GREEN_COLOR}Setting up CockroachDB for MovieLens${NO_COLOR}\n"
    "$DIR/movie-rating-system/util/import_db.py" "$DIR/MovieLens/"
fi

exit 0