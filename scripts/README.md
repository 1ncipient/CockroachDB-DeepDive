# Movie Rating System Setup Guide

This guide provides step-by-step instructions for setting up and running the Movie Rating System with multiple databases (CockroachDB, PostgreSQL, and MariaDB).

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Docker (optional, for containerized databases)
- Git

## Environment Setup

1. First, copy the `.env.template` to create your `.env` file:
   ```bash
   cp .env.template .env
   ```

2. Update the `.env` file with your database credentials:

## Database Installation

1. Install the databases using the provided script:
   ```bash
   chmod +x ./scripts/install-databases.sh
   ./scripts/install-databases.sh
   ```

   This script will:
   - Install PostgreSQL
   - Install MariaDB
   - Set up the necessary system dependencies

2. For CockroachDB:
   - Sign up for a free cluster at [CockroachDB Cloud](https://www.cockroachlabs.com/get-started-cockroachdb/)
   - Create a new cluster
   - Get your connection string and update it in the `.env` file

## Data Import

1. Download and process the MovieLens dataset:
   ```bash
   chmod +x ./scripts/dataset-setup.sh
   ./scripts/dataset-setup.sh
   ```
   -r option will download a fresh copy of the data

   This script will:
   - Download the MovieLens dataset
   - Process and transform the data
   - Create the necessary CSV files for import

2. Set up the database schemas and import the data:
   ```bash
   chmod +x ./scripts/database-setup.sh
   ./scripts/database-setup.sh
   ```

    Options:
    -r: reset the databases
    -d: specify the databases to install

    without -d options, all databases will be installed and the data will be imported

   This script will:
   - Create the necessary databases
   - Create users with appropriate permissions
   - Set up the required extensions

## Troubleshooting

### Database Connection Issues

1. PostgreSQL:
   - Check if the service is running:
     ```bash
     sudo systemctl status postgresql
     ```
   - Verify connection:
     ```bash
     psql -U your_user -d moviedb -h localhost
     ```

2. MariaDB:
   - Check if the service is running:
     ```bash
     sudo systemctl status mariadb
     ```
   - Verify connection:
     ```bash
     mysql -u your_user -p moviedb
     ```

3. CockroachDB:
   - Verify your connection string in the `.env` file
   - Test connection:
     ```bash
     cockroach sql --url your_connection_string
     ```

### Common Issues

1. Permission Denied:
   ```bash
   sudo chmod +x scripts/*.sh
   ```

2. Database Already Exists:
   ```bash
   # PostgreSQL
   dropdb moviedb
   # MariaDB
   mysql -u root -p -e "DROP DATABASE moviedb"
   ```

3. Port Conflicts:
   - PostgreSQL default port: 5432
   - MariaDB default port: 3306
   - Check for port usage:
     ```bash
     sudo lsof -i :port_number
     ```

## Features

The Movie Rating System includes:
- Multi-database support (CockroachDB, PostgreSQL, MariaDB)
- Movie search with various filters
- Movie details with genome tags
- Actor information
- Performance metrics and query analysis
- Export functionality for search results

## Database-Specific Notes

### PostgreSQL
- Supports full-text search
- Uses JSONB for efficient JSON storage
- Materialized views for genome scores

### MariaDB
- Uses JSON columns for metadata
- Full-text search capabilities
- Optimized for transactional queries

### CockroachDB
- Distributed SQL database
- High availability and scalability
- Compatible with PostgreSQL wire protocol

## Maintenance

1. Update database schemas:
   ```bash
   python -m movieRatingSystem.models.movie_models
   ```

2. Clear logs:
   ```bash
   rm -f logs/*.log
   ```

## Security Notes

1. Never commit your `.env` file
2. Regularly update database passwords
3. Use appropriate SSL modes for production
4. Keep your dependencies updated

## Additional Resources

- [MovieLens Dataset](https://grouplens.org/datasets/movielens/)
- [CockroachDB Documentation](https://www.cockroachlabs.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MariaDB Documentation](https://mariadb.org/documentation/) 