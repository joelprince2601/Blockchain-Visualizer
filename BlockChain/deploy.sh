#!/bin/bash

# Build and deploy the blockchain application

# Build Docker image
docker-compose build

# Run tests
docker-compose run blockchain python run_tests.py

# If tests pass, deploy
if [ $? -eq 0 ]; then
    echo "Tests passed. Deploying..."
    docker-compose up -d
else
    echo "Tests failed. Deployment aborted."
    exit 1
fi 