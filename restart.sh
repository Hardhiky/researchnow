#!/bin/bash
echo "Stopping services..."
docker compose stop backend web-frontend

echo "Cleaning caches..."
sudo rm -rf backend/__pycache__
sudo rm -rf web-frontend/.next
sudo rm -rf web-frontend/node_modules/.cache

echo "Starting services..."
docker compose up -d backend web-frontend

echo "Waiting for services to start..."
sleep 5

echo "Done! Services are starting up."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Check logs with:"
echo "  sudo docker compose logs -f backend"
echo "  sudo docker compose logs -f web-frontend"
