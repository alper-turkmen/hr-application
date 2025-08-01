#!/bin/bash

docker-compose exec web python manage.py migrate

if [ $? -eq 0 ]; then
    echo "Database migrations completed"
else
    echo "Database migrations failed"
    exit 1
fi
