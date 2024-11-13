# README: Configuration of Python and Docker Environment

# Introduction
# This guide will set up a Python virtual environment, configure Docker for Airflow, 
# and run services with Docker Compose.

# Prerequisites
# Python 3.3+ : Check installation
python --version

# Docker: Ensure Docker is installed and running

# Steps

# 1. Create a Python Virtual Environment
# Create the environment
python -m venv <env_name>

# Activate the environment
# On Windows:
<env_name>\Scripts\activate

# On macOS/Linux:
source <env_name>/bin/activate

# 2. Prepare Environment for Docker
# Check available memory
docker run --rm "debian:bookworm-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'

# Configure Airflow user (Linux only)
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env

# For other systems, ignore the AIRFLOW_UID warning or manually create .env
# with the following content:
# AIRFLOW_UID=50000

# 3. Run Docker Compose
# Navigate to the directory with docker-compose.yml
cd src/app

# Start services
docker-compose up


# 4.Finally, you would be able to access PostgreSQL and Apache Airflow through the browser using these links:
# Access Airflow at:
http://localhost:8080/home

# Access PostgreSQL at:
http://127.0.0.1:5050/browser/