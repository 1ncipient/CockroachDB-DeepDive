#!/bin/bash

SCRIPT_PATH=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT_PATH")

MOVIE_LENS_PATH="$DIR/../MovieLens"

GREEN_COLOR='\033[1;32m'
RED_COLOR='\033[0;31m'
NO_COLOR='\033[0m'

# sudo apt update

DEPENDENCIES="unzip python3"
dpkg -s ${DEPENDENCIES} 1> /dev/null
if [ "$?" -eq "1" ]
then
  echo "Installing $DEPENDENCIES"
  
  apt-get install -y ${DEPENDENCIES}
fi

# Download and extract MovieLens dataset and the full movie metadata
if  [[ $1 = "-r" ]]; then
    echo -e "\n${GREEN_COLOR}Downloading fresh copy of data${NO_COLOR}\n"

    find "$MOVIE_LENS_PATH/" -maxdepth 1 ! -name data_processing.ipynb ! -name data_process.py -type f -delete

    echo -e "\n${GREEN_COLOR}Downloading movie metadata${NO_COLOR}\n"
    curl -L -o "$MOVIE_LENS_PATH/movie_metadata.zip" https://www.kaggle.com/api/v1/datasets/download/thanhnghth/movielens-metadata-datasets

    echo -e "\n${GREEN_COLOR}Downloading movie data${NO_COLOR}\n"
    curl -L -o "$MOVIE_LENS_PATH/ml-latest.zip" https://files.grouplens.org/datasets/movielens/ml-latest.zip

    unzip "$MOVIE_LENS_PATH/movie_metadata.zip" -d "$MOVIE_LENS_PATH/"
    unzip -j "$MOVIE_LENS_PATH/ml-latest.zip" -d "$MOVIE_LENS_PATH/"

    rm "$MOVIE_LENS_PATH/ml-latest.zip" "$MOVIE_LENS_PATH/movie_metadata.zip" "$MOVIE_LENS_PATH/keywords.csv" "$MOVIE_LENS_PATH/tags.csv"

    echo -e "\n${GREEN_COLOR}Movie data download complete${NO_COLOR}\n"
fi

echo -e "\n${GREEN_COLOR}Processing movie data${NO_COLOR}\n"
"$MOVIE_LENS_PATH/data_process.py" "$MOVIE_LENS_PATH/"

exit 0
