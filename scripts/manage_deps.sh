#!/bin/bash
# Dependencies management script for Glad Tidings School Management Portal

# Exit on error
set -e

# Parse command line arguments
ACTION=$1
DEV=$2

case $ACTION in
    install)
        echo "Installing dependencies..."
        pip install -r requirements.txt
        if [ "$DEV" == "--dev" ]; then
            echo "Installing development dependencies..."
            pip install pytest pytest-django coverage flake8 black isort
        fi
        ;;

    update)
        echo "Updating dependencies..."
        pip install --upgrade -r requirements.txt
        if [ "$DEV" == "--dev" ]; then
            echo "Updating development dependencies..."
            pip install --upgrade pytest pytest-django coverage flake8 black isort
        fi
        ;;

    freeze)
        echo "Freezing current dependencies..."
        pip freeze > requirements.txt
        echo "Dependencies frozen to requirements.txt"
        ;;

    *)
        echo "Usage: ./manage_deps.sh [install|update|freeze] [--dev]"
        echo "  install: Install dependencies from requirements.txt"
        echo "  update: Update all dependencies"
        echo "  freeze: Freeze current dependencies to requirements.txt"
        echo "  --dev: Include development dependencies"
        exit 1
        ;;
esac

echo "Done!"
