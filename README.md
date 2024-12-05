# Movie Rating System

A multi-database movie rating and recommendation system.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd movie-rating-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
```
Then edit `.env` with your database credentials and configuration.

## Database Configuration

The system supports multiple SQL databases:

### CockroachDB (Default)
- Set `COCKROACH_DATABASE_URL` in `.env`
- Format: `cockroachdb://user:password@host:port/dbname?sslmode=disable`

### PostgreSQL (Optional)
- Set `POSTGRES_DATABASE_URL` in `.env`
- Format: `postgresql://user:password@host:port/dbname`

### MariaDB (Optional)
- Set `MARIADB_DATABASE_URL` in `.env`
- Format: `mysql+pymysql://user:password@host:port/dbname`
- Requires PyMySQL package for MySQL protocol support
- Uses UTF-8 character set by default

## Connection Pool Settings

You can configure the database connection pool in `.env`:
- `DB_POOL_SIZE`: Maximum number of permanent connections
- `DB_MAX_OVERFLOW`: Maximum number of temporary connections
- `DB_POOL_TIMEOUT`: Seconds to wait before timing out
- `DB_POOL_RECYCLE`: Seconds before connections are recycled

## Running the Application

```bash
python application.py
```

The application will be available at `http://localhost:5000`

## Features

- Multi-database support (CockroachDB, PostgreSQL, MariaDB)
- Configurable connection pooling
- Environment-based configuration
- Colored logging
- Client-side sorting
- Server-side pagination
- Advanced search filters