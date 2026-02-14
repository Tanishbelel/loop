#!/bin/bash

echo "==================================="
echo "Project Intelligence System Setup"
echo "==================================="
echo ""

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo ""
echo "Step 2: Creating database migrations..."
python manage.py makemigrations

echo ""
echo "Step 3: Applying migrations..."
python manage.py migrate

echo ""
echo "Step 4: Loading sample data..."
python manage.py load_sample_data

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Sample Login Credentials:"
echo ""
echo "Project Manager:"
echo "  Username: pm_john"
echo "  Password: password123"
echo ""
echo "Employees:"
echo "  Username: alice / bob / carol"
echo "  Password: password123"
echo ""
echo "To start the server, run:"
echo "  python manage.py runserver"
echo ""
echo "To run tests:"
echo "  python manage.py test main"
echo ""
echo "Access API at: http://localhost:8000/api/"
echo "Access Admin at: http://localhost:8000/admin/"
echo "==================================="
