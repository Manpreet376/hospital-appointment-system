# Python base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Requirements copy karo
COPY backend/requirements.txt .

# Install karo
RUN pip install -r requirements.txt

# Poora project copy karo
COPY backend/ .

# Port expose karo
EXPOSE 5000

# App chalao
CMD ["python", "app.py"]