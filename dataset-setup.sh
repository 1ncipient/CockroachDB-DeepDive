#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
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

    find "$DIR/MovieLens/" -maxdepth 1 ! -name data_processing.ipynb ! -name data_process.py -type f -delete

    echo -e "\n${GREEN_COLOR}Downloading movie metadata${NO_COLOR}\n"
    curl -L -o "$DIR/MovieLens/movie_metadata.zip" https://www.kaggle.com/api/v1/datasets/download/thanhnghth/movielens-metadata-datasets

    echo -e "\n${GREEN_COLOR}Downloading movie data${NO_COLOR}\n"
    curl -L -o "$DIR/MovieLens/ml-latest.zip" https://files.grouplens.org/datasets/movielens/ml-latest.zip

    unzip "$DIR/MovieLens/movie_metadata.zip" -d "$DIR/MovieLens/"
    unzip -j "$DIR/MovieLens/ml-latest.zip" -d "$DIR/MovieLens/"

    rm "$DIR/MovieLens/ml-latest.zip" "$DIR/MovieLens/movie_metadata.zip" "$DIR/MovieLens/keywords.csv"

    echo -e "\n${GREEN_COLOR}Movie data download complete${NO_COLOR}\n"
fi

echo -e "\n${GREEN_COLOR}Processing movie data${NO_COLOR}\n"
"$DIR/MovieLens/data_process.py" "$DIR/MovieLens/"

exit 0
