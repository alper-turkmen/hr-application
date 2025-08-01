#!/bin/bash

echo "Stopping existing containers..."
docker-compose down

echo "Building and starting services..."
docker-compose up -d --build

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose exec web python manage.py migrate

if [ $? -eq 0 ]; then
    echo "Database migrations completed successfully!"
else
    echo "Database migrations failed. Retrying..."
    sleep 5
    docker-compose exec web python manage.py migrate
fi

echo "adding initial activity data"
docker-compose exec web python manage.py populate_activity_data

if [ $? -eq 0 ]; then
    echo "Activity data populated successfully!"
else
    echo "Activity data population failed."
fi

echo "adding initial data "
docker-compose exec web python manage.py populate_initial_data

if [ $? -eq 0 ]; then
    echo "Initial data populated successfully!"
else
    echo "Initial data population failed."
fi

echo "You can create a superuser by running"
echo "docker-compose exec web python manage.py createsuperuser"

docker-compose ps

echo ""
echo "  - Django App: http://localhost:8000"
echo "  - Flower (Celery Monitor): http://localhost:5555"
echo "  - PostgreSQL: localhost:5433"
echo "  - Redis: localhost:6379"
echo "  - Run migrations: docker-compose exec web python manage.py migrate"
echo "  - Create superuser: docker-compose exec web python manage.py createsuperuser"