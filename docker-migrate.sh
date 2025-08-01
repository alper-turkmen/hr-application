#!/bin/bash

docker-compose exec web python manage.py migrate

if [ $? -eq 0 ]; then
    echo "Database migrations completed"
    
    echo "adding initial activity data"
    docker-compose exec web python manage.py populate_activity_data
    
    if [ $? -eq 0 ]; then
        echo "Activity data populated successfully!"
    else
        echo "Activity data population failed."
    fi

    echo "adding initial data (companies, users, candidates, etc.)..."
    docker-compose exec web python manage.py populate_initial_data
    
    if [ $? -eq 0 ]; then
        echo "Initial data populated successfully!"
    else
        echo "Initial data population failed."
    fi
else
    echo "Database migrations failed"
    exit 1
fi
