name: Hospital App CI/CD

on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flask flask-sqlalchemy flask-login werkzeug requests reportlab pillow

      - name: Test App
        run: |
          cd backend
          python -c "from app import app; print('✅ App loaded successfully!')"