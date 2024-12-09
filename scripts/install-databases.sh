#!/bin/bash

GREEN_COLOR='\033[1;32m'
RED_COLOR='\033[0;31m'
NO_COLOR='\033[0m'

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install PostgreSQL
install_postgresql() {
    echo -e "\n${GREEN_COLOR}Installing PostgreSQL...${NO_COLOR}\n"
    
    # Add PostgreSQL repository
    if ! command_exists psql; then
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        
        # Start PostgreSQL service
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
        # Create database and user
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS moviedb;"
        sudo -u postgres psql -c "DROP USER IF EXISTS johnny;"
        sudo -u postgres psql -c "CREATE DATABASE moviedb;"
        sudo -u postgres psql -c "CREATE USER johnny WITH PASSWORD 'u418o8MMX4i7xdMi9cHk-Q';"
        sudo -u postgres psql -c "ALTER USER johnny WITH SUPERUSER;"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE moviedb TO johnny;"

        # Restart PostgreSQL to apply changes
        sudo systemctl restart postgresql
        
        echo -e "${GREEN_COLOR}PostgreSQL installed and configured successfully!${NO_COLOR}\n"
    else
        echo -e "${GREEN_COLOR}PostgreSQL is already installed${NO_COLOR}\n"
    fi
}

# Install MariaDB
install_mariadb() {
    echo -e "\n${GREEN_COLOR}Installing MariaDB...${NO_COLOR}\n"
    
    if ! command_exists mariadb; then
        sudo apt-get update
        sudo apt-get install -y mariadb-server libmariadb-dev
        
        # Start MariaDB service
        sudo systemctl start mariadb
        sudo systemctl enable mariadb
        
        # Secure the installation
        sudo mysql_secure_installation <<EOF

y
password
password
y
y
y
y
EOF
        
        # Create database and user with proper privileges
        sudo mysql -e "DROP DATABASE IF EXISTS moviedb;"
        sudo mysql -e "DROP USER IF EXISTS 'johnny'@'localhost';"
        sudo mysql -e "CREATE DATABASE moviedb;"
        sudo mysql -e "CREATE USER 'johnny'@'localhost' IDENTIFIED BY 'u418o8MMX4i7xdMi9cHk-Q';"
        sudo mysql -e "GRANT ALL PRIVILEGES ON moviedb.* TO 'johnny'@'localhost';"
        sudo mysql -e "GRANT SUPER ON *.* TO 'johnny'@'localhost';"
        sudo mysql -e "FLUSH PRIVILEGES;"
        
        echo -e "${GREEN_COLOR}MariaDB installed and configured successfully!${NO_COLOR}\n"
    else
        echo -e "${GREEN_COLOR}MariaDB is already installed${NO_COLOR}\n"
    fi
}

# Main installation process
echo -e "${GREEN_COLOR}Starting database installations...${NO_COLOR}\n"

# Check if script is run with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED_COLOR}Please run this script with sudo${NO_COLOR}"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y curl wget gnupg2 software-properties-common

# Install databases
install_postgresql
install_mariadb

echo -e "${GREEN_COLOR}All database installations completed!${NO_COLOR}\n" 