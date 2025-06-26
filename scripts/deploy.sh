#!/bin/bash
# Deployment script for Glad Tidings School Management Portal

# Exit on error
set -e

echo "Starting deployment process..."

# Pull the latest code
git pull origin main

# Activate virtual environment (create if it doesn't exist)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

source .venv/bin/activate || source .venv/Scripts/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart the service (example using systemd)
# echo "Restarting service..."
# sudo systemctl restart gladschool

echo "Deployment completed successfully!"
