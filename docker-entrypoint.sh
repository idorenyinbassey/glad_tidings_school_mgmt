#!/bin/bash
set -e

# Docker entrypoint script for Django application
echo "🚀 Starting Glad Tidings School Management System..."

# Wait for database to be ready (if using PostgreSQL)
if [ "$DB_HOST" ]; then
    echo "⏳ Waiting for database at $DB_HOST:$DB_PORT..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
    done
    echo "✅ Database is ready!"
fi

# Wait for Redis to be ready (if using Redis)
if [ "$REDIS_URL" ]; then
    echo "⏳ Waiting for Redis..."
    # Extract host and port from Redis URL
    REDIS_HOST=$(echo $REDIS_URL | sed 's/redis:\/\/\([^:]*\).*/\1/')
    REDIS_PORT=$(echo $REDIS_URL | sed 's/.*:\([0-9]*\).*/\1/' | grep -o '[0-9]*' | tail -1)
    REDIS_PORT=${REDIS_PORT:-6379}
    
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
        sleep 1
    done
    echo "✅ Redis is ready!"
fi

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (only in development)
if [ "$DJANGO_SETTINGS_MODULE" = "glad_school_portal.settings_dev" ]; then
    echo "👤 Creating development superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
"
fi

echo "🎉 Setup completed! Starting application..."

# Execute the command passed to the script
exec "$@"
